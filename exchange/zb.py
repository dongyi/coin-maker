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
import urllib.request


from lib.util import retry_call


class zb_api:

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
        try:
            SHA_secret = self.__digest(self.mysecret)
            sign = self.__hmacSign(params, SHA_secret)
            self.jm = sign
            reqTime = (int)(time.time() * 1000)
            params += '&sign=%s&reqTime=%d' % (sign, reqTime)
            url = 'https://trade.zb.com/api/' + path + '?' + params
            req = urllib.request.Request(url)
            res = urllib.request.urlopen(req, timeout=2)
            doc = json.loads(res.read())
            return doc
        except Exception as ex:
            print(sys.stderr, 'zb request ex: ', ex)
            return None

    @retry_call(3)
    def query_account(self):
        params = "accesskey=" + self.mykey + "&method=getAccountInfo"
        path = 'getAccountInfo'

        obj = self.__api_call(path, params)
        # print obj
        return obj

    @retry_call(3)
    def trades(self):
        params = "accesskey=" + self.mykey + "&method=getAccountInfo"
        path = "trades"
        obj = self.__api_call(path, params)
        return obj


if __name__ == '__main__':
    access_key = 'access_key'
    access_secret = 'access_secret'

    api = zb_api(access_key, access_secret)

    print(api.query_account())
