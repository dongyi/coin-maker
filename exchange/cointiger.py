from enum import Enum, unique

import time
import hmac
import hashlib

from lib.util import *

try:
    from urllib import urlencode
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urlencode
    from urllib.parse import urljoin
import requests

try:
    from Crypto.Cipher import AES
    import getpass, ast, json

    encrypted = True
except ImportError:
    encrypted = False

BUY_ORDERBOOK = 'buy'
SELL_ORDERBOOK = 'sell'
BOTH_ORDERBOOK = 'both'

TRADING_URL = 'https://api.cointiger.com/exchange/trading/api'
MARKET_URL = 'https://api.cointiger.com/exchange/trading/api/market'
WSS_URL = 'wss://api.cointiger.com/exchange-market/ws'


class CoinConst(Enum):
    SYSTEM_EXCEPTION = 100001
    SYSTEM_UPGRADING = 100002
    REQUEST_EXCEPTION = 100003


class CoinTiger:
    """
    cointiger API client
    """

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def api_query(self, method, option=None):
        """
        Queries CoinTiger with given method and options
        :param method:
        :param option:
        :return:
        """
        if not option:
            options = {}

    def get_balance(self):
        pass

    def get_order_history(self, market, count):
        pass

    def get_order_trade(self):
        pass

    def get_orderbook(self, market, depth_type, depth=20):
        pass

    def order(self):
        pass