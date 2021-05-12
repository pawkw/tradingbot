import logging
import time
import hmac
import hashlib
from urllib.parse import urlencode
import requests
import websocket
import json
import threading
import keys

logger = logging.getLogger()

class BinanceFuturesClient:
    def __init__(self, public_key, secret_key, testing):
        if testing:
            self.base_url = keys.sandbox
            self.base_wss = keys.sandboxWebsocket
        else:
            self.base_url = keys.actual
            self.base_wss = keys.actualWebsocket

        self.public_key = public_key
        self.secret_key = secret_key

        self.headers = {'X-MBX-APIKEY': self.public_key}

        self.prices = dict()
        self.id = 1
        self.ws_thread = None

        logger.info('Initialized '+'sandbox at Binance.' if testing else 'actual trading client at Binance.')

        t = threading.Thread(target=self.start_websocket())
        logger.debug('Thread set.')
        t.start()
        logger.debug('Thread running.')

    def generate_signature(self, params):
        return hmac.new(self.secret_key.encode(), urlencode(params).encode(), hashlib.sha256).hexdigest()

    def make_request(self, method, endpoint, params):
        if method == 'GET':
            response = requests.get(self.base_url+endpoint, params=params, headers=self.headers)
        elif method == 'POST':
            response = requests.post(self.base_url + endpoint, params=params, headers=self.headers)
        elif method == 'DELETE':
            response = requests.delete(self.base_url + endpoint, params=params, headers=self.headers)
        else:
            raise ValueError()

        if response.status_code == 200:
            return response.json()
        else:
            logger.error('Error while making %s request to %s: %s (%d)',
                         method, endpoint, response.json(), response.status_code)
            return None

    def get_contracts(self):
        exchange_info = self.make_request('GET', '/fapi/v1/exchangeInfo', None)

        contracts = dict()
        if exchange_info is not None:
            for contract in exchange_info['symbols']:
                contracts[contract['pair']] = contract

        return contracts

    def get_historical_data(self, symbol, interval):
        params = dict()
        params['symbol'] = symbol
        params['interval'] = interval
        params['limit'] = 1000

        response = self.make_request('GET', '/fapi/v1/klines', params)
        candles = []

        if response is not None:
            for candle in response:
                candles.append([candle[0], float(candle[1]), float(candle[2]), float(candle[3]),
                               float(candle[4]), float(candle[5])])
        return candles

    def get_bid_ask(self, symbol):
        params = dict()
        params['symbol'] = symbol
        response = self.make_request('GET', '/fapi/v1/ticker/bookTicker', params)

        if response is not None:
            if symbol not in self.prices:
                self.prices[symbol] = {'bid': float(response['bidPrice']),
                                       'ask': float(response['askPrice'])}
            else:
                self.prices[symbol]['bid'] = float(response['bidPrice'])
                self.prices[symbol]['ask'] = float(response['askPrice'])

        return self.prices[symbol]

    def get_balances(self):
        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self.generate_signature(data)

        balances = dict()

        account_data = self.make_request('GET', '/fapi/v1/account', data)

        if account_data:
            for asset in account_data['assets']:
                balances[asset['asset']] = asset
        return balances

    def place_order(self, symbol, side, quantity, order_type, price=None, tif=None):
        data = dict()
        data['symbol'] = symbol
        data['side'] = side
        data['quantity'] = quantity
        data['type'] = order_type
        if price is not None:
            data['price'] = price
        if tif is not None:
            data['timeInForce'] = tif
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self.generate_signature(data)

        status = self.make_request('POST', '/fapi/v1/order', data)

        return status


    def cancel_order(self, symbol, order_id):
        data = dict()
        data['orderId'] = order_id
        data['symbol'] = symbol
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self.generate_signature(data)

        status = self.make_request('DELETE', '/fapi/v1/order', data)

        return status


    def order_status(self, symbol, order_id):
        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['symbol'] = symbol
        data['orderId'] = order_id
        data['signature'] = self.generate_signature(data)

        status = self.make_request('GET', '/fapi/v1/order', data)

        return status

    def get_open_orders(self):
        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self.generate_signature(data)

        status = self.make_request('GET', '/fapi/v1/openOrders', data)

        return status

    def start_websocket(self):
        self.ws_thread = websocket.WebSocketApp(self.base_wss, on_open=self.on_open, on_error=self.on_error, on_close=self.on_close,
                                                on_message=self.on_message)
        self.ws_thread.run_forever()

    def on_open(self, ws):
        logger.info("Opened websocket: %s", self.base_wss)
        self.subscribe_to_channel('BTCUSDT')
        return

    def on_error(self, ws, msg):
        logger.error("Websocket error on %s: %s", self.base_wss, msg)
        return

    def on_close(self, ws):
        logger.warning("Websocket %s closed.", self.base_wss)
        return

    def on_message(self, ws, msg):
        print(msg)

        data = json.loads(msg)

        if "e" in data:
            if data['e'] == 'bookTicker':
                symbol = data['s']
                if symbol not in self.prices:
                    self.prices[symbol] = {'bid': float(data['b']),
                                           'ask': float(data['a'])}
                else:
                    self.prices[symbol]['bid'] = float(data['b'])
                    self.prices[symbol]['ask'] = float(data['a'])

        return

    def subscribe_to_channel(self, symbol):
        data = dict()
        data['method'] = 'SUBSCRIBE'
        data['params'] = []
        data['params'].append(symbol.lower()+'@bookTicker')
        data['id'] = self.id
        self.id += 1

        self.ws_thread.send(json.dumps(data))
        return
