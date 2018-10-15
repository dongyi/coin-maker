import hmac
import hashlib
import json
import requests

# doc: https://github.com/Biboxcom/API_Docs/wiki


def getSign(data, secret):
    result = hmac.new(secret.encode("utf-8"), data.encode("utf-8"), hashlib.md5).hexdigest()
    return result


def doApiRequestWithApikey(url, cmds, api_key, api_secret):
    s_cmds = json.dumps(cmds)
    sign = getSign(s_cmds, api_secret)
    r = requests.post(url, data={'cmds': s_cmds, 'apikey': api_key, 'sign': sign})
    print(r.text)


def post_order(api_key, api_secret, cmds):
    url = "https://api.bibox.com/v1/orderpending"
    doApiRequestWithApikey(url, cmds, api_key, api_secret)


api_key = 'your api_key'
api_secret = 'your api_secret'

account_type = 0
order_type = 2
order_side = 1
pair = 'BIX_ETH'
price = 0.00081600
amount = 0.1

cmds = [
    {
        'cmd': "orderpending/trade",
        'body': {
            'pair': pair,
            'account_type': account_type,
            'order_type': order_type,
            'order_side': order_side,
            'price': price,
            'amount': amount
        }
    }
]

post_order(api_key, api_secret, cmds)
