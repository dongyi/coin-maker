import requests

import json
import time
import hmac
import hashlib

from lib.util import retry_call
from lib.util import load_api_key

BASE_URL = 'https://api.big.one/'

API_BASE_PATH = ''

API_PATH_DICT = {
    # GET
    'account': '/accounts',
    'account_currency': '/accounts/{currency}',
    'markets': '/markets/{symbol}',
    'all_markets': '/markets',
    'order_books': '/markets/{symbol}/book',
    'trades': '/markets/{symbol}/trades',
    'orders': '/orders{?market,limit}',
    'order_by_id': '/orders/{id}',
    'trades_list': '/trades{?market,limit,offset}',
    'deposit': '/deposits{?currency,limit,offset}',
    'withdraw_list': '/withdrawals{?currency,limit,offset}',

    # POST
    'order': '/orders',
    'batch_cancel': '/orders/cancel',
    'withdraws': '/withdrawals',

    # DELETE
    'delete_order': '/orders/{id}',
}


class Client:
    def __init__(self, access_key=None, secret_key=None):
        if access_key and secret_key:
            self.auth = Auth(access_key, secret_key)
        else:
            print("provide key please")

    def getHistory(self, market='1stcny'):
        result = self.get('k', {'market': market})

    def getBalance(self):
        result = self.get('members', sigrequest=True)
        balance = {}
        for record in result["accounts"]:
            balance[record["currency"]] = float(record["balance"])
            balance[record["currency"] + "_locked"] = float(record["locked"])
        return balance

    def getTickers(self, market='1stcny'):
        ticker = self.get('tickers', {'market': market})["ticker"]
        result = {"vol": float(ticker["vol"]), "buy": float(ticker["buy"]),
                  "last": float(ticker["last"]),
                  "sell": float(ticker["sell"])}
        return result

    def getOpenOrders(self, market='1stcny'):
        orders = self.get('orders', {'market': market}, True)
        openorders = []
        for order in orders:
            openorders.append({"amount": float(order["volume"]), "type": order["side"], "price": float(order["price"]),
                               "id": order["id"], })
        return openorders

    def getOrderBook(self, market='1stcny', limit=20):
        orderbooks = self.get('order_book', {'market': market}, True)
        asks = []
        for record in orderbooks["asks"][:limit]:
            asks.append([float(record['price']), float(record['volume'])])

        bids = []
        for record in orderbooks["bids"][:limit]:
            bids.append([float(record['price']), float(record['volume'])])
        return {"bids": bids, "asks": asks[::-1]}

    def getMyTradeList(self, market='1stcny'):
        return self.get('trades', {'market': market}, True)

    def submitOrder(self, params):
        return self.post('orders', params)

    def get_api_path(self, name):
        path_pattern = API_PATH_DICT[name]
        return path_pattern % API_BASE_PATH

    @retry_call(3)
    def get(self, name, params=None, sigrequest=False):
        verb = "GET"
        path = self.get_api_path(name)
        if "%s" in path:
            path = path % params["market"]
        if sigrequest:
            signature, query = self.auth.sign_params(verb, path, params)
            query = self.auth.urlencode(query)
            url = "%s%s?%s&signature=%s" % (BASE_URL, path, query, signature)
        else:
            url = "%s%s?" % (BASE_URL, path)
        resp = requests.get(url, timeout=10)
        data = resp.text

        if len(data):
            return json.loads(data)

    def post(self, name, params=None):
        verb = "POST"
        path = self.get_api_path(name)
        signature, data = self.auth.sign_params(verb, path, params)
        url = "%s%s" % (BASE_URL, path)
        data.update({"signature": signature})

        resp = requests.post(url, data, timeout=10)
        data = resp.text
        if len(data):
            return json.loads(data.decode)


# --------------------------------------------------------------------------------------


class Auth:
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key

    def urlencode(self, params):
        keys = params.keys()
        keys = sorted(keys)
        query = ''
        for key in keys:
            value = params[key]
            if key != "orders":
                query = "%s&%s=%s" % (query, key, value) if len(query) else "%s=%s" % (key, value)
            else:
                d = {key: params[key]}
                for v in value:
                    ks = v.keys()
                    ks = sorted(ks)
                    for k in ks:
                        item = "orders[][%s]=%s" % (k, v[k])
                        query = "%s&%s" % (query, item) if len(query) else "%s" % item
        return query

    def sign(self, verb, path, params=None):
        query = self.urlencode(params)
        msg = ("|".join([verb, path, query])).encode('utf-8')
        signature = hmac.new(self.secret_key.encode('utf-8'), msg=msg, digestmod=hashlib.sha256).hexdigest()

        return signature

    def sign_params(self, verb, path, params=None):
        if not params:
            params = {}
        params.update({'tonce': int(1000 * time.time()), 'access_key': self.access_key})
        signature = self.sign(verb, path, params)

        return signature, params


if __name__ == '__main__':
    api_key, secret_key = load_api_key('bigone')
    client = Client(api_key, secret_key)
