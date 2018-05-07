from enum import Enum, unique

import time
import hmac
import hashlib
import requests

from lib.util import *

try:
    from urllib import urlencode
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urlencode
    from urllib.parse import urljoin

try:
    from Crypto.Cipher import AES
    import getpass, ast, json

    encrypted = True
except ImportError:
    encrypted = False

TRADING_URL = 'https://api.cointiger.com/exchange/trading/api'
MARKET_URL = 'https://api.cointiger.com/exchange/trading/api/market'
WSS_URL = 'wss://api.cointiger.com/exchange-market/ws'


class CoinConst(Enum):
    SYSTEM_EXCEPTION = 100001
    SYSTEM_UPGRADING = 100002
    REQUEST_EXCEPTION = 100003
    BUY_ORDERBOOK = 'buy'
    SELL_ORDERBOOK = 'sell'
    BOTH_ORDERBOOK = 'both'


class CoinTiger:
    """
    cointiger API client
    """

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def sign(self, args):
        if not args:
            args = {}

        sorted_args = sorted(args.items(), key=lambda x: x[0])
        sorted_args_txt = ''.join(['{}{}'.format(k, v) for k, v in sorted_args])

        pdata = (sorted_args_txt + self.api_secret).encode()

        apisign2 = hmac.new(self.api_secret.encode("utf-8"), pdata, hashlib.sha512).hexdigest()

        return apisign2

    def get(self, entry, args=None):
        """
        Queries CoinTiger with given method and options
        :param method:
        :param option:
        :return:
        """
        if 'time' not in args:
            args['time'] = int(time.time() * 1000)

        args['sign'] = self.sign(args)
        args['api_key'] = self.api_key
        req_args = '&'.join(['{}={}'.format(k, v) for k, v in args.items()])
        req_url = entry + '?' + req_args

        return json.loads(requests.get(req_url).text)

    def get_balance(self, coin=None):
        req_entry = TRADING_URL + '/user/balance'
        option = {}
        ret = self.get(req_entry, option)
        assert ret['code'] == '0'
        total_balance = ret['data']
        return total_balance if coin is None else [i for i in total_balance if i['coin'] == coin]

    def get_order_history(self, market, count):
        pass

    def get_order_trade(self):
        pass

    def get_orderbook(self, market, depth_type, depth=20):
        pass

    def order(self):
        pass
