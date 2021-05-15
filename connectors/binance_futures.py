import logging
import time

import hmac
import hashlib
from urllib.parse import urlencode

import requests
import websocket
import json
import threading
import typing

import binance_keys
from models import *

logger = logging.getLogger()


class BinanceFuturesClient:
    def __init__(self, public_key: str, secret_key: str, testing: bool):
        if testing:
            self._base_url = binance_keys.sandbox
            self._base_wss = binance_keys.sandboxWebsocket
        else:
            self._base_url = binance_keys.actual
            self._base_wss = binance_keys.actualWebsocket

        self._public_key = public_key
        self._secret_key = secret_key

        self._headers = {'X-MBX-APIKEY': self._public_key}

        self.prices = dict()
        self.contracts = self.get_contracts()
        self.balances = self.get_balances()

        self._ws_id = 1
        self._ws_thread = None

        logger.info('Initialized '+'sandbox at Binance.' if testing else 'actual trading client at Binance.')

        t = threading.Thread(target=self._start_websocket)
        logger.debug('Thread set.')
        t.start()
        logger.debug('Thread running.')

    def _generate_signature(self, params: typing.Dict) -> str:
        return hmac.new(self._secret_key.encode(), urlencode(params).encode(), hashlib.sha256).hexdigest()

    def _make_request(self, method: str, endpoint: str, params: typing.Dict):
        try:
            if method == 'GET':
                response = requests.get(self._base_url+endpoint, params=params, headers=self._headers)
            elif method == 'POST':
                response = requests.post(self._base_url + endpoint, params=params, headers=self._headers)
            elif method == 'DELETE':
                response = requests.delete(self._base_url + endpoint, params=params, headers=self._headers)
            else:
                raise ValueError()
        except Exception as e:
            logger.error('Error while making %s request to %s: %s',
                         method, endpoint, e)
            return None

        if response.status_code == 200:
            return response.json()
        else:
            logger.error('Error while making %s request to %s: %s (%d)',
                         method, endpoint, response.json(), response.status_code)
            return None

    def get_contracts(self) -> typing.Dict[str, Contract]:
        exchange_info = self._make_request('GET', '/fapi/v1/exchangeInfo', dict())

        contracts = dict()
        if exchange_info is not None:
            for contract in exchange_info['symbols']:
                contracts[contract['pair']] = Contract(contract, 'Binance')

        return contracts

    def get_historical_data(self, contract: Contract, interval: str) -> typing.List[Candle]:
        params = dict()
        params['symbol'] = contract.symbol
        params['interval'] = interval
        params['limit'] = 1000

        response = self._make_request('GET', '/fapi/v1/klines', params)
        candles = []

        if response is not None:
            for candle in response:
                candles.append(Candle(candle, interval, 'Binance'))
        return candles

    def get_bid_ask(self, contract: Contract) -> typing.Dict[str, float]:
        params = dict()
        params['symbol'] = contract.symbol
        response = self._make_request('GET', '/fapi/v1/ticker/bookTicker', params)

        if response is not None:
            if contract.symbol not in self.prices:
                self.prices[contract.symbol] = {'bid': float(response['bidPrice']),
                                                'ask': float(response['askPrice'])}
            else:
                self.prices[contract.symbol]['bid'] = float(response['bidPrice'])
                self.prices[contract.symbol]['ask'] = float(response['askPrice'])

            return self.prices[contract.symbol]

    def get_balances(self) -> typing.Dict[str, Balance]:
        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self._generate_signature(data)

        balances = dict()

        account_data = self._make_request('GET', '/fapi/v1/account', data)

        if account_data:
            for asset in account_data['assets']:
                balances[asset['asset']] = Balance(asset, 'Binance')
        return balances

    def place_order(self, contract: Contract, side: str, quantity: float, order_type: str, price=None, tif=None) -> OrderStatus:
        data = dict()
        data['symbol'] = contract.symbol
        data['side'] = side
        data['quantity'] = round(round(quantity / contract.lot_size) * contract.lot_size, 8)
        data['type'] = order_type
        if price is not None:
            data['price'] = round(round(price / contract.tick_size) * contract.tick_size, 8)
        if tif is not None:
            data['timeInForce'] = tif
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self._generate_signature(data)

        status = self._make_request('POST', '/fapi/v1/order', data)

        if status is not None:
            status = OrderStatus(status)

        return status

    def cancel_order(self, contract: Contract, order_id: int) -> OrderStatus:
        data = dict()
        data['orderId'] = order_id
        data['symbol'] = contract.symbol
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self._generate_signature(data)

        status = self._make_request('DELETE', '/fapi/v1/order', data)

        if status is not None:
            status = OrderStatus(status)

        return status

    def get_order_status(self, contract: Contract, order_id: int) -> OrderStatus:
        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['symbol'] = contract.symbol
        data['orderId'] = order_id
        data['signature'] = self._generate_signature(data)

        status = self._make_request('GET', '/fapi/v1/order', data)

        if status is not None:
            status = OrderStatus(status)

        return status

    def get_open_orders(self):
        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self._generate_signature(data)

        status = self._make_request('GET', '/fapi/v1/openOrders', data)

        return status

    def _start_websocket(self):
        self.ws_thread = websocket.WebSocketApp(self._base_wss, on_open=self._on_open, on_error=self._on_error,
                                                on_close=self._on_close, on_message=self._on_message)
        while True:
            try:
                self.ws_thread.run_forever()
            except Exception as e:
                logger.error('Lost connection to Websocket: %s', e)
            time.sleep(2.0)

    def _on_open(self, ws):
        logger.info("Opened websocket: %s", self._base_wss)
        self.subscribe_to_channel(list(self.contracts.values()), 'bookTicker')
        return

    def _on_error(self, ws, msg: str):
        logger.error("Websocket error on %s: %s", self._base_wss, msg)
        return

    def _on_close(self, ws):
        logger.warning("Websocket %s closed.", self._base_wss)
        return

    def _on_message(self, ws, msg: str):
        print(ws, msg)

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
            print()
        return

    def subscribe_to_channel(self, contracts: typing.List[Contract], channel: str):
        data = dict()
        data['method'] = 'SUBSCRIBE'
        data['params'] = []

        for contract in contracts:
            data['params'].append(contract.symbol.lower()+'@'+channel)
            data['id'] = self._ws_id
            self._ws_id += 1

        try:
            self.ws_thread.send(json.dumps(data))
        except Exception as e:
            logger.error('Error while subscribing to %d feeds of %s: %s', channel, len(contracts), e)
        return
