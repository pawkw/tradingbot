# # Much to do.

import logging
import time

import hmac
import hashlib
import base64
from requests.auth import AuthBase
from urllib.parse import urlencode

import requests
import websocket
import json
import threading
import typing

import coinbase_keys
from models import *

logger = logging.getLogger()


class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        # signature_b64 = signature.digest().encode('base64').rstrip('\n')
        signature_b64 = signature.hexdigest().rstrip('\n')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request


class CoinBaseFuturesClient:
    def __init__(self, public_key: str, secret_key: str, passphrase: str, testing: bool):
        if testing:
            self._base_url = coinbase_keys.sandbox
            self._base_wss = coinbase_keys.sandboxWebsocket
        else:
            self._base_url = coinbase_keys.actual
            self._base_wss = coinbase_keys.actualWebsocket

        self._public_key = public_key
        self._secret_key = secret_key
        self._passphrase = passphrase
        self._auth = CoinbaseExchangeAuth(self._public_key, self._secret_key, self._passphrase)
        self._ws_thread = None
        self._ws_id = 1

        self.contracts = self.get_contracts()
        self.balances = self.get_balances()
        self.prices = dict()

        # t = threading.Thread(target=self._start_websocket)
        # logger.debug('Thread set.')
        # t.start()
        # logger.debug('Thread running.')

    def _generate_signature(self, params: typing.Dict) -> str:
        return hmac.new(self._secret_key.encode(), urlencode(params).encode(), hashlib.sha256).hexdigest()

    def _make_request(self, method: str, endpoint: str, params: typing.Dict):
        try:
            if method == 'GET':
                response = requests.get(self._base_url + endpoint, params=params, headers=self._headers)
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

    def get_contracts(self):
        logger.debug('Getting user.')
        r = requests.get(self._base_url + '/user', auth=self._auth)
        logger.debug('Received user.')
        print(r.json())
        return []

    def get_balances(self):
        return []


if __name__ == '__main__':
    client = CoinBaseFuturesClient(coinbase_keys.ACTUAL_APIKEY, coinbase_keys.ACTUAL_APISECRET,
                                   coinbase_keys.ACTUAL_PASSPHRASE, True)
    client.get_contracts()
