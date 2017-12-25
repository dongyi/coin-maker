import http.client
import urllib
import json
import hashlib
import time


def buildMySign(params, secretKey):
    sign = ''
    for key in sorted(params.keys()):
        sign += key + '=' + str(params[key]) + '&'
    data = sign + 'secret_key=' + secretKey
    return hashlib.md5(data.encode("utf8")).hexdigest().upper()


def httpGet(url, resource, params=''):
    conn = http.client.HTTPSConnection(url, timeout=10)
    conn.request("GET", resource + '?' + params)
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    return json.loads(data)


def httpPost(url, resource, params):
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
    }
    conn = http.client.HTTPSConnection(url, timeout=10)
    temp_params = urllib.parse.urlencode(params)
    conn.request("POST", resource, temp_params, headers)
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    params.clear()
    conn.close()
    return data


class OKCoinFuture:
    def __init__(self, url, apikey, secretkey):
        self.__url = url
        self.__apikey = apikey
        self.__secretkey = secretkey

    # OKCOIN期货行情信息
    def future_ticker(self, symbol, contractType):
        FUTURE_TICKER_RESOURCE = "/api/v1/future_ticker.do"
        params = ''
        if symbol:
            params += '&symbol=' + symbol if params else 'symbol=' + symbol
        if contractType:
            params += '&contract_type=' + contractType if params else 'contract_type=' + symbol
        return httpGet(self.__url, FUTURE_TICKER_RESOURCE, params)

    # OKCoin期货市场深度信息
    def future_depth(self, symbol, contractType, size):
        FUTURE_DEPTH_RESOURCE = "/api/v1/future_depth.do"
        params = ''
        if symbol:
            params += '&symbol=' + symbol if params else 'symbol=' + symbol
        if contractType:
            params += '&contract_type=' + contractType if params else 'contract_type=' + symbol
        if size:
            params += '&size=' + size if params else 'size=' + size
        return httpGet(self.__url, FUTURE_DEPTH_RESOURCE, params)

    # OKCoin期货交易记录信息
    def future_trades(self, symbol, contractType):
        FUTURE_TRADES_RESOURCE = "/api/v1/future_trades.do"
        params = ''
        if symbol:
            params += '&symbol=' + symbol if params else 'symbol=' + symbol
        if contractType:
            params += '&contract_type=' + contractType if params else 'contract_type=' + symbol
        return httpGet(self.__url, FUTURE_TRADES_RESOURCE, params)

    # OKCoin期货指数
    def future_index(self, symbol):
        FUTURE_INDEX = "/api/v1/future_index.do"
        params = ''
        if symbol:
            params = 'symbol=' + symbol
        return httpGet(self.__url, FUTURE_INDEX, params)

    # 获取美元人民币汇率
    def exchange_rate(self):
        EXCHANGE_RATE = "/api/v1/exchange_rate.do"
        return httpGet(self.__url, EXCHANGE_RATE, '')

    # 获取预估交割价
    def future_estimated_price(self, symbol):
        FUTURE_ESTIMATED_PRICE = "/api/v1/future_estimated_price.do"
        params = ''
        if symbol:
            params = 'symbol=' + symbol
        return httpGet(self.__url, FUTURE_ESTIMATED_PRICE, params)

    # 期货全仓账户信息
    def future_userinfo(self):
        FUTURE_USERINFO = "/api/v1/future_userinfo.do?"
        params = {}
        params['api_key'] = self.__apikey
        params['sign'] = buildMySign(params, self.__secretkey)
        return httpPost(self.__url, FUTURE_USERINFO, params)

    # 期货全仓持仓信息
    def future_position(self, symbol, contractType):
        FUTURE_POSITION = "/api/v1/future_position.do?"
        params = {
            'api_key': self.__apikey,
            'symbol': symbol,
            'contract_type': contractType
        }
        params['sign'] = buildMySign(params, self.__secretkey)
        return httpPost(self.__url, FUTURE_POSITION, params)

    # 期货下单
    def future_trade(self, symbol, contractType, price='', amount='', tradeType='', matchPrice='', leverRate=''):
        FUTURE_TRADE = "/api/v1/future_trade.do?"
        params = {
            'api_key': self.__apikey,
            'symbol': symbol,
            'contract_type': contractType,
            'amount': amount,
            'type': tradeType,
            'match_price': matchPrice,
            'lever_rate': leverRate
        }
        if price:
            params['price'] = price
        params['sign'] = buildMySign(params, self.__secretkey)
        return httpPost(self.__url, FUTURE_TRADE, params)

    # 期货批量下单
    def future_batchTrade(self, symbol, contractType, orders_data, leverRate):
        FUTURE_BATCH_TRADE = "/api/v1/future_batch_trade.do?"
        params = {
            'api_key': self.__apikey,
            'symbol': symbol,
            'contract_type': contractType,
            'orders_data': orders_data,
            'lever_rate': leverRate
        }
        params['sign'] = buildMySign(params, self.__secretkey)
        return httpPost(self.__url, FUTURE_BATCH_TRADE, params)

    # 期货取消订单
    def future_cancel(self, symbol, contractType, orderId):
        FUTURE_CANCEL = "/api/v1/future_cancel.do?"
        params = {
            'api_key': self.__apikey,
            'symbol': symbol,
            'contract_type': contractType,
            'order_id': orderId
        }
        params['sign'] = buildMySign(params, self.__secretkey)
        return httpPost(self.__url, FUTURE_CANCEL, params)

    # 期货获取订单信息
    def future_orderinfo(self, symbol, contractType, orderId, status, currentPage, pageLength):
        FUTURE_ORDERINFO = "/api/v1/future_order_info.do?"
        params = {
            'api_key': self.__apikey,
            'symbol': symbol,
            'contract_type': contractType,
            'order_id': orderId,
            'status': status,
            'current_page': currentPage,
            'page_length': pageLength
        }
        params['sign'] = buildMySign(params, self.__secretkey)
        return httpPost(self.__url, FUTURE_ORDERINFO, params)

    # 期货逐仓账户信息
    def future_userinfo_4fix(self):
        FUTURE_INFO_4FIX = "/api/v1/future_userinfo_4fix.do?"
        params = {'api_key': self.__apikey}
        params['sign'] = buildMySign(params, self.__secretkey)
        return httpPost(self.__url, FUTURE_INFO_4FIX, params)

    # 期货逐仓持仓信息
    def future_position_4fix(self, symbol, contractType, type1):
        FUTURE_POSITION_4FIX = "/api/v1/future_position_4fix.do?"
        params = {
            'api_key': self.__apikey,
            'symbol': symbol,
            'contract_type': contractType,
            'type': type1
        }
        params['sign'] = buildMySign(params, self.__secretkey)
        return httpPost(self.__url, FUTURE_POSITION_4FIX, params)


class OKCoinSpot:
    def __init__(self, url, apikey, secretkey):
        self.__url = url
        self.__apikey = apikey
        self.__secretkey = secretkey

    # 获取OKCOIN现货行情信息
    def ticker(self, symbol=''):
        TICKER_RESOURCE = "/api/v1/ticker.do"
        params = ''
        if symbol:
            params = 'symbol=%(symbol)s' % {'symbol': symbol}
        return httpGet(self.__url, TICKER_RESOURCE, params)

    # 获取OKCOIN现货市场深度信息
    def depth(self, symbol=''):
        DEPTH_RESOURCE = "/api/v1/depth.do"
        params = ''
        if symbol:
            params = 'symbol=%(symbol)s' % {'symbol': symbol}
        return httpGet(self.__url, DEPTH_RESOURCE, params)

        # 获取OKCOIN现货历史交易信息

    def trades(self, symbol=''):
        TRADES_RESOURCE = "/api/v1/trades.do"
        params = ''
        if symbol:
            params = 'symbol=%(symbol)s' % {'symbol': symbol}
        return httpGet(self.__url, TRADES_RESOURCE, params)

    # 获取用户现货账户信息
    def userinfo(self):
        USERINFO_RESOURCE = "/api/v1/userinfo.do"
        params = {}
        params['api_key'] = self.__apikey
        params['sign'] = buildMySign(params, self.__secretkey)
        return httpPost(self.__url, USERINFO_RESOURCE, params)

    # 现货交易
    def trade(self, symbol, tradeType, price='', amount=''):
        TRADE_RESOURCE = "/api/v1/trade.do"
        params = {
            'api_key': self.__apikey,
            'symbol': symbol,
            'type': tradeType
        }
        if price:
            params['price'] = price
        if amount:
            params['amount'] = amount

        params['sign'] = buildMySign(params, self.__secretkey)
        return httpPost(self.__url, TRADE_RESOURCE, params)

    # 现货批量下单
    def batchTrade(self, symbol, tradeType, orders_data):
        BATCH_TRADE_RESOURCE = "/api/v1/batch_trade.do"
        params = {
            'api_key': self.__apikey,
            'symbol': symbol,
            'type': tradeType,
            'orders_data': orders_data
        }
        params['sign'] = buildMySign(params, self.__secretkey)
        return httpPost(self.__url, BATCH_TRADE_RESOURCE, params)

    # 现货取消订单
    def cancelOrder(self, symbol, orderId):
        CANCEL_ORDER_RESOURCE = "/api/v1/cancel_order.do"
        params = {
            'api_key': self.__apikey,
            'symbol': symbol,
            'order_id': orderId
        }
        params['sign'] = buildMySign(params, self.__secretkey)
        return httpPost(self.__url, CANCEL_ORDER_RESOURCE, params)

    # 现货订单信息查询
    def orderinfo(self, symbol, orderId):
        ORDER_INFO_RESOURCE = "/api/v1/order_info.do"
        params = {
            'api_key': self.__apikey,
            'symbol': symbol,
            'order_id': orderId
        }
        params['sign'] = buildMySign(params, self.__secretkey)
        return httpPost(self.__url, ORDER_INFO_RESOURCE, params)

    # 现货批量订单信息查询
    def ordersinfo(self, symbol, orderId, tradeType):
        ORDERS_INFO_RESOURCE = "/api/v1/orders_info.do"
        params = {
            'api_key': self.__apikey,
            'symbol': symbol,
            'order_id': orderId,
            'type': tradeType
        }
        params['sign'] = buildMySign(params, self.__secretkey)
        return httpPost(self.__url, ORDERS_INFO_RESOURCE, params)

    # 现货获得历史订单信息
    def orderHistory(self, symbol, status, currentPage, pageLength):
        ORDER_HISTORY_RESOURCE = "/api/v1/order_history.do"
        params = {
            'api_key': self.__apikey,
            'symbol': symbol,
            'status': status,
            'current_page': currentPage,
            'page_length': pageLength
        }
        params['sign'] = buildMySign(params, self.__secretkey)
        return httpPost(self.__url, ORDER_HISTORY_RESOURCE, params)


if __name__ == '__main__':

    # 初始化apikey，secretkey,url
    with open("secrets.json") as secrets_file:
        secrets = json.load(secrets_file)
        secrets_file.close()
        apikey, secretkey = secrets["okex"]['apikey'], secrets["okex"]['secretkey']

    okcoinRESTURL = 'www.okex.com'  # 请求注意：国内账号需要 修改为 www.okcoin.cn

    # 现货API
    okcoinSpot = OKCoinSpot(okcoinRESTURL, apikey, secretkey)

    # 期货API
    okcoinFuture = OKCoinFuture(okcoinRESTURL, apikey, secretkey)

    print(u' 现货行情 ')
    print(okcoinSpot.ticker('btc_usd'))

    print(u' 现货深度 ')
    print(okcoinSpot.depth('btc_usd'))

    # print (u' 现货历史交易信息 ')
    # print (okcoinSpot.trades())

    # print (u' 用户现货账户信息 ')
    # print (okcoinSpot.userinfo())

    # print (u' 现货下单 ')
    # print (okcoinSpot.trade('ltc_usd','buy','0.1','0.2'))

    # print (u' 现货批量下单 ')
    # print (okcoinSpot.batchTrade('ltc_usd','buy','[{price:0.1,amount:0.2},{price:0.1,amount:0.2}]'))

    # print (u' 现货取消订单 ')
    # print (okcoinSpot.cancelOrder('ltc_usd','18243073'))

    # print (u' 现货订单信息查询 ')
    # print (okcoinSpot.orderinfo('ltc_usd','18243644'))

    # print (u' 现货批量订单信息查询 ')
    # print (okcoinSpot.ordersinfo('ltc_usd','18243800,18243801,18243644','0'))

    # print (u' 现货历史订单信息查询 ')
    # print (okcoinSpot.orderHistory('ltc_usd','0','1','2'))

    # print (u' 期货行情信息')
    # print (okcoinFuture.future_ticker('ltc_usd','this_week'))

    # print (u' 期货市场深度信息')
    # print (okcoinFuture.future_depth('btc_usd','this_week','6'))

    # print (u'期货交易记录信息')
    # print (okcoinFuture.future_trades('ltc_usd','this_week'))

    # print (u'期货指数信息')
    # print (okcoinFuture.future_index('ltc_usd'))

    # print (u'美元人民币汇率')
    # print (okcoinFuture.exchange_rate())

    # print (u'获取预估交割价')
    # print (okcoinFuture.future_estimated_price('ltc_usd'))

    # print (u'获取全仓账户信息')
    # print (okcoinFuture.future_userinfo())

    # print (u'获取全仓持仓信息')
    # print (okcoinFuture.future_position('ltc_usd','this_week'))

    # print (u'期货下单')
    # print (okcoinFuture.future_trade('ltc_usd','this_week','0.1','1','1','0','20'))

    # print (u'期货批量下单')
    # print (okcoinFuture.future_batchTrade('ltc_usd','this_week','[{price:0.1,amount:1,type:1,match_price:0},{price:0.1,amount:3,type:1,match_price:0}]','20'))

    # print (u'期货取消订单')
    # print (okcoinFuture.future_cancel('ltc_usd','this_week','47231499'))

    # print (u'期货获取订单信息')
    # print (okcoinFuture.future_orderinfo('ltc_usd','this_week','47231812','0','1','2'))

    # print (u'期货逐仓账户信息')
    # print (okcoinFuture.future_userinfo_4fix())

    # print (u'期货逐仓持仓信息')
    # print (okcoinFuture.future_position_4fix('ltc_usd','this_week',1))
