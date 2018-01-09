__author__ = 'Ziyang'

"""
//......
    String ACCESS_KEY = "your_access_key";//例子:33b4e193-3386-4c9c-8242-98f39ebb6115
    String SECRET_KEY = "your_secret_key";//例子:99254c4d-91be-438f-9a7c-8c0b51227f6e
    params.put("accesskey", ACCESS_KEY);// 这个需要加入签名,放前面
    //算出digest:4609e4359b0b6f50dddc0b63aa01eaa7
    String digest = EncryDigestUtil.digest(SECRET_KEY);

    // 参数按照ASCII值排序
    // (首先比较参数名的第一个字母，按abcdefg顺序排列，若遇到相同首字母，则看第二个字母，以此类推)
    //参数排序例子:accesskey=33b4e193-3386-4c9c-8242-98f39ebb6115&amount=1&currency=ltc_qc&method=order&price=0.1&tradeType=1
    //算出sign:4609e4359b0b6f50dddc0b63aa01eaa7
    String sign = EncryDigestUtil.hmacSign(MapSort.toStringMap(params), digest);
    String method = params.get("method");

    // 加入验证
    params.put("sign", sign);
    params.put("reqTime", System.currentTimeMillis() + "");
    String url = "请求地址:" + URL_PREFIX + method + " 参数:" + params;
    String json = "";
    try {
        json = HttpUtilManager.getInstance().requestHttpPost(URL_PREFIX, method, params);
    } catch (HttpException | IOException e) {
        log.error("获取交易json异常", e);
    }
//......
"""

import json
import hashlib
import struct
import time
import sys
import requests
import websocket
import hashlib
import struct

from threading import Thread

from lib.util import retry_call
from lib.util import load_api_key

zb_usd_url = "wss://api.zb.com:9999/websocket"
zb_all_symbols = ["ltc_btc"]


class ZB_Sub_Spot_Api(object):
    """基于Websocket的API对象"""

    def __init__(self):
        """Constructor"""
        self.apiKey = ''  # 用户名
        self.secretKey = ''  # 密码

        self.ws_sub_spot = None  # websocket应用对象  现货对象

    # ----------------------------------------------------------------------
    def reconnect(self):
        """重新连接"""
        # 首先关闭之前的连接
        self.close()

        # 再执行重连任务
        self.ws_sub_spot = websocket.WebSocketApp(self.host,
                                                  on_message=self.onMessage,
                                                  on_error=self.onError,
                                                  on_close=self.onClose,
                                                  on_open=self.onOpen)

        self.thread = Thread(target=self.ws_sub_spot.run_forever)
        self.thread.start()

    # ----------------------------------------------------------------------
    def connect_Subpot(self, apiKey, secretKey, trace=False):
        self.host = zb_usd_url
        self.apiKey = apiKey
        self.secretKey = secretKey

        websocket.enableTrace(trace)

        self.ws_sub_spot = websocket.WebSocketApp(self.host,
                                                  on_message=self.onMessage,
                                                  on_error=self.onError,
                                                  on_close=self.onClose,
                                                  on_open=self.onOpen)

        self.thread = Thread(target=self.ws_sub_spot.run_forever)
        self.thread.start()

    # ----------------------------------------------------------------------
    def readData(self, evt):
        """解压缩推送收到的数据"""
        # # 创建解压器
        # decompress = zlib.decompressobj(-zlib.MAX_WBITS)

        # # 将原始数据解压成字符串
        # inflated = decompress.decompress(evt) + decompress.flush()

        # 通过json解析字符串
        data = json.loads(evt)

        return data

    # ----------------------------------------------------------------------
    def close(self):
        """关闭接口"""
        if self.thread and self.thread.isAlive():
            self.ws_sub_spot.close()
            self.thread.join()

    # ----------------------------------------------------------------------
    def onMessage(self, ws, evt):
        """信息推送"""
        print(evt)

    # ----------------------------------------------------------------------
    def onError(self, ws, evt):
        """错误推送"""
        print('onError')
        print(evt)

    # ----------------------------------------------------------------------
    def onClose(self, ws):
        """接口断开"""
        print('onClose')

    # ----------------------------------------------------------------------
    def onOpen(self, ws):
        """接口打开"""
        print('onOpen')

    # ----------------------------------------------------------------------
    def subscribeSpotTicker(self, symbol_pair):
        # 现货的 ticker
        symbol_pair = symbol_pair.replace('_', '')
        req = "{'event':'addChannel','channel':'%s_ticker'}" % symbol_pair
        self.ws_sub_spot.send(req)

    # ----------------------------------------------------------------------
    def subscribeSpotDepth(self, symbol_pair):
        # 现货的 市场深度
        symbol_pair = symbol_pair.replace('_', '')
        req = "{'event':'addChannel','channel':'%s_depth'}" % symbol_pair
        self.ws_sub_spot.send(req)

    # ----------------------------------------------------------------------
    def subscribeSpotTrades(self, symbol_pair):
        symbol_pair = symbol_pair.replace('_', '')
        req = "{'event':'addChannel','channel':'%s_trades'}" % symbol_pair
        self.ws_sub_spot.send(req)

    # ----------------------------------------------------------------------
    def __fill(self, value, lenght, fillByte):
        if len(value) >= lenght:
            return value
        else:
            fillSize = lenght - len(value)
        return value + chr(fillByte) * fillSize

    # ----------------------------------------------------------------------
    def __doXOr(self, s, value):
        slist = list(s)
        for index in range(len(slist)):
            slist[index] = chr(ord(slist[index]) ^ value)
        return "".join(slist)

    # ----------------------------------------------------------------------
    def __hmacSign(self, aValue, aKey):
        keyb = struct.pack("%ds" % len(aKey), aKey)
        value = struct.pack("%ds" % len(aValue), aValue)
        k_ipad = self.__doXOr(keyb, 0x36)
        k_opad = self.__doXOr(keyb, 0x5c)
        k_ipad = self.__fill(k_ipad, 64, 54)
        k_opad = self.__fill(k_opad, 64, 92)
        m = hashlib.md5()
        m.update(k_ipad)
        m.update(value)
        dg = m.digest()

        m = hashlib.md5()
        m.update(k_opad)
        subStr = dg[0:16]
        m.update(subStr)
        dg = m.hexdigest()
        return dg

    # ----------------------------------------------------------------------
    def __digest(self, aValue):
        value = struct.pack("%ds" % len(aValue), aValue)

        h = hashlib.sha256()
        h.update(value)
        dg = h.hexdigest()
        return dg

    # ----------------------------------------------------------------------
    def generateSign(self, params):
        """生成签名"""
        '''
        {"accesskey":"0f39fb8b-d95d-4afe-b2a9-94f5f4d9fdb5","channel":"getaccountinfo","event":"addChannel"}
        '''
        l = []
        for key in sorted(params.keys()):
            l.append('"%s":"%s"' % (key, params[key]))
        sign = ','.join(l)
        sign = '{' + sign + '}'

        SHA_secret = self.__digest(self.secretKey)
        return self.__hmacSign(sign, SHA_secret)
        # return hashlib.md5(sign.encode('utf-8')).hexdigest().upper()

    # ----------------------------------------------------------------------
    def sendTradingRequest(self, channel, params):
        """发送交易请求"""
        # 在参数字典中加上api_key和签名字段
        params['accesskey'] = self.apiKey
        params['channel'] = channel
        params['event'] = "addChannel"

        params['sign'] = self.generateSign(params)

        # 使用json打包并发送
        j = json.dumps(params)

        # 若触发异常则重连
        try:
            self.ws_sub_spot.send(j)
        except websocket.WebSocketConnectionClosedException:
            pass

            # ----------------------------------------------------------------------

    def spotTrade(self, symbol_pair, type_, price, amount):
        """现货委托"""
        symbol_pair = symbol_pair.replace('_', '')
        params = {}
        params['tradeType'] = str(type_)
        params['price'] = str(price)
        params['amount'] = str(amount)

        channel = symbol_pair.lower() + "_order"

        self.sendTradingRequest(channel, params)

    # ----------------------------------------------------------------------
    def spotCancelOrder(self, symbol_pair, orderid):
        """现货撤单"""
        symbol_pair = symbol_pair.replace('_', '')
        params = {}
        params['id'] = str(orderid)

        channel = symbol_pair.lower() + "_cancelorder"

        self.sendTradingRequest(channel, params)

    # ----------------------------------------------------------------------
    def spotUserInfo(self):
        """查询现货账户"""
        channel = 'getaccountinfo'
        self.sendTradingRequest(channel, {})

    # ----------------------------------------------------------------------
    def spotOrderInfo(self, symbol_pair, orderid):
        """查询现货委托信息"""
        symbol_pair = symbol_pair.replace('_', '')
        params = {}
        params['id'] = str(orderid)

        channel = symbol_pair.lower() + "_getorder"

        self.sendTradingRequest(channel, params)

    # ----------------------------------------------------------------------
    def spotGetOrders(self, symbol_pair, orderid):
        pass


class ZB:

    def __init__(self, mykey, mysecret):
        self.mykey = mykey
        self.mysecret = mysecret
        self.jm = ''

    def __fill(self, value, lenght, fillByte):
        if len(value) >= lenght:
            return value
        else:
            fillSize = lenght - len(value)
        return value + chr(fillByte) * fillSize

    def __doXOr(self, s, value):
        slist = list(s.decode('utf-8'))
        for index in range(len(slist)):
            slist[index] = chr(ord(slist[index]) ^ value)
        return "".join(slist)

    def __hmacSign(self, aValue, aKey):
        keyb = struct.pack("%ds" % len(aKey), aKey.encode('utf-8'))
        value = struct.pack("%ds" % len(aValue), aValue.encode('utf-8'))
        k_ipad = self.__doXOr(keyb, 0x36)
        k_opad = self.__doXOr(keyb, 0x5c)
        k_ipad = self.__fill(k_ipad, 64, 54)
        k_opad = self.__fill(k_opad, 64, 92)
        m = hashlib.md5()
        m.update(k_ipad.encode('utf-8'))
        m.update(value)
        dg = m.digest()

        m = hashlib.md5()
        m.update(k_opad.encode('utf-8'))
        subStr = dg[0:16]
        m.update(subStr)
        dg = m.hexdigest()
        return dg

    def __digest(self, aValue):
        value = struct.pack("%ds" % len(aValue), aValue.encode('utf-8'))
        print(value)
        h = hashlib.sha1()
        h.update(value)
        dg = h.hexdigest()
        return dg

    def __api_call(self, path, params=''):
        SHA_secret = self.__digest(self.mysecret)
        sign = self.__hmacSign(params, SHA_secret)
        self.jm = sign
        reqTime = int((time.time() * 1000))
        params += '&sign=%s&reqTime=%d' % (sign, reqTime)
        url = 'http://api.zb.com/data/v1/' + path + '?' + params
        res = requests.get(url)
        txt = res.text
        doc = json.loads(txt)
        return doc

    @retry_call(3)
    def query_account(self):
        params = "accesskey=" + self.mykey + "&method=getAccountInfo"
        path = 'getAccountInfo'

        obj = self.__api_call(path, params)
        # print obj
        return obj

    @retry_call(3)
    def trades(self, pair):
        params = "market={}".format(pair)
        path = "trades"
        obj = self.__api_call(path, params)
        return obj


def test_api():
    key, secret = load_api_key('zb')
    api = ZB(key, secret)
    print(api.trades('1stbtc'))


if __name__ == '__main__':
    access_key = 'access_key'
    access_secret = 'access_secret'

    api = ZB(access_key, access_secret)

    print(api.query_account())
