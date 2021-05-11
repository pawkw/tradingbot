import logging
import time
import hmac
import hashlib
from urllib.parse import urlencode
import requests
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
        logger.info('Initialized '+'sandbox at Binance.' if testing else 'actual trading client at Binance.')

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
