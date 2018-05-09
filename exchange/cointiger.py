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

        apisign = hmac.new(self.api_secret.encode("utf-8"), pdata, hashlib.sha512).hexdigest()

        return apisign

    def post(self, entry, args=None):
        """
        :param entry: 请求地址
        :param args:  请求参数
        :return:
        """
        if 'time' not in args:
            args['time'] = int(time.time() * 1000)

        args['sign'] = self.sign(args)
        args['api_key'] = self.api_key

        return json.loads(requests.post(entry, data=args).text)

    def delete(self, entry, args=None):
        """
        :param entry: 请求地址
        :param args:  请求参数
        :return:
        """
        if 'time' not in args:
            args['time'] = int(time.time() * 1000)
        args['sign'] = self.sign(args)
        args['api_key'] = self.api_key

        req_args = '&'.join(['{}={}'.format(k, v) for k, v in args.items()])
        req_url = entry + '?' + req_args

        req = requests.delete(req_url)
        return json.loads(req.text)

    def get(self, entry, args=None):
        """
        Queries CoinTiger with given method and options
        :param method: 请求地址
        :param option: 请求参数
        :return:
        """
        if 'time' not in args:
            args['time'] = int(time.time() * 1000)

        args['sign'] = self.sign(args)
        args['api_key'] = self.api_key
        req_args = '&'.join(['{}={}'.format(k, v) for k, v in args.items()])
        req_url = entry + '?' + req_args
        return json.loads(requests.get(req_url).text)

    @retry_call(3)
    def get_balance(self, coin=None):
        """
        获取账户余额
        :param coin: 交易对，不传就是返回全部余额
        :return:
        """
        req_entry = TRADING_URL + '/user/balance'
        options = {}
        ret = self.get(req_entry, options)
        assert ret['code'] == '0', ret
        total_balance = ret['data']
        return total_balance if coin is None else [i for i in total_balance if i['coin'] == coin]

    @retry_call(3)
    def get_order_history(self, market, offset, limit):
        """
        自己的委托历史
        :param market: 交易对
        :param offset: 起始
        :param limit:  返回条目数
        :return:
        """
        req_entry = TRADING_URL + '/order/history'
        options = {'symbol': market,
                   'offset': offset,
                   'limit': limit}

        ret = self.get(req_entry, options)
        assert ret['code'] == '0', ret
        return ret['data']

    @retry_call(3)
    def get_trade_history(self, market, offset, limit):
        """
        自己有成交的订单
        :param market: 交易对
        :param offset: 起始
        :param limit:  返回条目数
        :return:
        """
        req_entry = TRADING_URL + '/order/trade '
        options = {'symbol': market,
                   'offset': offset,
                   'limit': limit}

        ret = self.get(req_entry, options)
        assert ret['code'] == '0', ret
        return ret['data']

    @retry_call(3)
    def get_order_trade(self, market, offset, limit):
        """
        自己的open orders
        :param market: 交易对
        :param offset: 起始
        :param limit:  返回条目数
        :return:
        """
        req_entry = TRADING_URL + '/order/new'
        options = {'symbol': market,
                   'offset': offset,
                   'limit': limit}

        ret = self.get(req_entry, options)
        assert ret['code'] == '0', ret
        return ret['data']

    @retry_call(3)
    def get_orderbook(self, market):
        """
        交易对当前的orderbook
        :param market: 交易对
        :return:
        """
        req_entry = MARKET_URL + '/depth'
        options = {'symbol': market, 'type': 'step1'}
        ret = self.get(req_entry, options)
        assert ret['code'] == '0', ret
        return ret['data']

    @fail_default('can not order now')
    def order(self, side, order_type, volume, capital_password, price, symbol):
        """
        下单
        :param side:                        开仓方向
        :param order_type:                  订单类型  1：限价单  2：市价单
        :param volume:                      订单数量
        :param capital_password:            资金密码
        :param price:                       订单价格
        :param symbol:                      交易对
        :return:                            订单id
        """
        req_entry = TRADING_URL + '/order'
        options = {'side': side,
                   'type': order_type,
                   'volume': volume,
                   'capital_password': capital_password,
                   'price': price,
                   'symbol': symbol}
        ret = self.post(req_entry, options)
        assert ret['code'] == '0', ret
        return ret['data']['order_id']

    @fail_default('can not cancel order now')
    def cancel_order(self, order_id, symbol):
        """
        撤单
        :param order_id:               订单id
        :param symbol:                 交易对
        :return:
        """
        req_entry = TRADING_URL + '/order'
        options = {
            'order_id': order_id,
            'symbol': symbol
        }
        ret = self.delete(req_entry, options)
        assert ret['code'] == '0', ret
