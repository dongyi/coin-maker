from enum import Enum, unique

import datetime
import pandas as pd
import hmac
import hashlib
import requests
import websocket
import gzip

from lib.util import *
from lib.notifier import send_mail
from io import BytesIO

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

TRADING_URL = 'https://api.cointiger.pro/exchange/trading/api'
MARKET_URL = 'https://api.cointiger.pro/exchange/trading/api/market'
WSS_URL = 'wss://api.cointiger.pro/exchange-market/ws'

TRADING_URL_V2 = 'https://api.cointiger.pro/exchange/trading/api/v2'


class CoinConst(Enum):
    SYSTEM_EXCEPTION = 100001
    SYSTEM_UPGRADING = 100002
    REQUEST_EXCEPTION = 100003
    BUY_ORDERBOOK = 'buy'
    SELL_ORDERBOOK = 'sell'
    BOTH_ORDERBOOK = 'both'


class CoinTigerWS:
    def __init__(self, symbol):
        self.symbol = symbol
        self.ws = websocket.WebSocketApp(
            WSS_URL,
            on_message=self._on_message,
            on_close=self._on_close,
            on_open=self._on_open,
            on_error=self._on_error,
            header=self._get_auth()
        )
        self.last_orderbook = {}

    def _on_message(self, ws, message):
        compressedstream = BytesIO(message)
        gzipper = gzip.GzipFile(fileobj=compressedstream)

        msg = json.loads(gzipper.read().decode())
        channel = msg.get('channel', '')
        if channel == 'market_{}_depth_step0'.format(self.symbol):
            if 'tick' not in msg:
                return
            buys = msg['tick']['buys']
            sells = msg['tick']['asks']
            current_orderbook = {'bid': buys[0], 'ask': sells[0]}
            if current_orderbook != self.last_orderbook:
                print("[depth] bid1:", buys[0], "ask1:", sells[0], datetime.datetime.now())
                self.last_orderbook = current_orderbook

        elif channel == 'market_{}_trade_ticker'.format(self.symbol):
            tick = msg['tick']
            for ticker in tick['data']:
                side = ticker['side']
                vol = ticker['vol']
                amount = ticker['amount']
                price = ticker['price']
                order_id = ticker['id']
                ds = ticker['ds']
                now = datetime.datetime.now()
                print("[ticker] : sid:{side}, vol:{vol}, amount: {amount}, price:{price}, order_id:{order_id}, ds:{ds} [{now}]".format(**locals()))

        else:
            if 'ping' in msg:
                ws.send(json.dumps({'pong': time.time()*1000}))

    def _on_close(self, ws):
        print("websocket close")

    def _on_open(self, ws):
        ws.send(json.dumps({
            'event': 'sub',
            'params': {
                'cb_id': 'test',
                'asks': 5,
                'bids': 5,
                'channel': 'market_{}_depth_step0'.format(self.symbol)
            }
        }))
        ws.send(json.dumps({
            'event': 'sub',
            'params': {
                'cb_id': 'test',
                'channel': 'market_{}_trade_ticker'.format(self.symbol)
            }
        }))
        print("init done")

    def _on_error(self, ws, error):
        print("websocket error ,", error)

    def _get_auth(self):
        return []


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

        return json.loads(requests.post(entry, data=args, timeout=10).text)

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

        req = requests.delete(req_url, timeout=10)
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
        raw_ret = requests.get(req_url, timeout=20).text
        return json.loads(raw_ret)

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
    def get_total_trade_history(self, symbol):
        """
        交易对的历史成交记录
        :param symbol:
        :return:
        """
        req_entry = MARKET_URL + '/history/trade'
        options = {
            'symbol': symbol,
            'size': 50
        }
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
        options = {'symbol': market, 'type': 'step0'}
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
        :return:                            订单id / 错误原因
        """
        req_entry = TRADING_URL + '/order'
        options = {
            'side': side,
            'type': order_type,
            'volume': volume,
            'capital_password': capital_password,
            'price': price,
            'symbol': symbol
        }
        print("open order:", options)
        ret = self.post(req_entry, options)
        return ret

    @fail_default('can not order now')
    def order_v2(self, side, order_type, volume, price, symbol):
        """
        下单
        :param side:                        开仓方向
        :param order_type:                  订单类型  1：限价单  2：市价单
        :param volume:                      订单数量
        :param price:                       订单价格
        :param symbol:                      交易对
        :return:                            订单id / 错误原因
        """
        req_entry = TRADING_URL_V2 + '/order'
        options = {
            'side': side,
            'type': order_type,
            'volume': volume,
            'price': price,
            'symbol': symbol
        }
        print("open order:", options)
        ret = self.post(req_entry, options)
        return ret

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
        return ret

    @fail_default('can not cancel order now')
    def cancel_order_v2(self, order_id_list, symbol):
        """
        撤单
        :param order_id:               订单id list
        :param symbol:                 交易对
        :return:
        """
        req_entry = TRADING_URL_V2 + '/order'
        options = {
            'orderIdList': order_id_list,
            'symbol': symbol
        }
        ret = self.delete(req_entry, options)
        return ret

    @retry_call(3)
    def get_order_history_V2(self, symbol, states, order_type='all', size=50, from_order_id=0, direct='prev'):
        """
        查询当前委托、历史委托
        :param symbol: 交易对
        :param states: 查询的订单状态组合，使用','分割	new ：新订单, part_filled ：部分成交, filled ：完全成交, canceled ：已撤销，expired：异常订单
        :param order_type:查询的订单类型组合，使用','分割  buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖
        :param size:查询记录大小	 	最多一次查询50条数据
        :param from_order_id:查询起始 ID （订单ID）
        :param direct:查询方向	prev 向前，next 向后
        :return:
        """
        req_entry = TRADING_URL_V2 + '/order/orders'
        options = {
            'symbol': symbol,
            'size': size,
            'states': states,
            'direct': direct,
        }
        if from_order_id != 0:
            options['from'] = from_order_id
        if order_type != 'all':
            options['type'] = order_type

        ret = self.get(req_entry, options)
        assert ret['code'] == '0', ret
        return ret['data']

    @retry_call(3)
    def get_match_result_v2(self, symbol, start_date, end_date, from_order_id=0, direct='prev', size=50):
        """
        查询当前成交， 历史成交
        :param symbol:
        :param start_date:
        :param end_date:
        :param from_order_id:
        :param direct:
        :param size:
        :return:
        """
        req_entry = TRADING_URL_V2 + '/order/match_results'
        options = {
            'symbol': symbol,
            'size': size,
            'start-date': start_date,
            'end_date': end_date,
            'direct': direct,
        }
        if from_order_id != 0:
            options['from'] = from_order_id
        ret = self.get(req_entry, options)
        assert ret['code'] == '0', ret
        return ret['data']

    @retry_call(3)
    def get_match_detail(self, symbol, order_id):
        """
        查询成交明细
        :param symbol:
        :param order_id:
        :return:
        """
        req_entry = TRADING_URL_V2 + '/order/make_detail'
        options = {
            'symbol':symbol,
            'order_id': order_id,
        }
        ret = self.get(req_entry, options)
        assert ret['code'] == '0', ret
        return ret['data']

    @retry_call(3)
    def dump_deal(self, symbol):
        total_list = []
        from_order_id = 0
        states = 'filled,part_filled,new,canceled,expired'
        while True:
            batch_data = self.get_order_history_V2(symbol, states, order_type='all', size=50,
                                                   from_order_id=from_order_id, direct='next')
            from_order_id = max([i['id'] for i in batch_data])
            total_list.extend(batch_data)
            if len(batch_data) < 50:
                break
            time.sleep(0.2)
        df = pd.DataFrame(total_list)
        df['cdatetime'] = df['ctime'].apply(lambda x: datetime.datetime.fromtimestamp(x / 1000))
        df['mdatetime'] = df['mtime'].apply(lambda x: datetime.datetime.fromtimestamp(x / 1000))
        df.to_csv('history.csv')

    def check_order_book(self, symbol):
        simple_log = open('simple_note.log', 'a')
        detail_log = open('detail_note.log', 'a')

        orderbook_list = self.get_orderbook(symbol)
        bids = ['{}:{}'.format(i[0], i[1]) for i in orderbook_list['depth_data']['tick']['buys'][:5]]
        asks = ['{}:{}'.format(i[0], i[1]) for i in orderbook_list['depth_data']['tick']['asks'][:5]]
        latest_trade = self.get_total_trade_history(symbol)['trade_data']
        note_simple = '[simple] bid1: {} ask1:{} latest:{} [{}]\n'.format(
            bids[0], asks[0], '{}'.format(latest_trade[0]['price']),
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        note_detail = '[detail] bid1: {} ask1:{} latest:{} [{}]\n'.format(
            ','.join(bids), ','.join(asks), '{}'.format(latest_trade[0]['price']),
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        if not (float(bids[0].split(':')[0]) <= latest_trade[0]['price'] <= float(asks[0].split(':')[0])):
            send_mail("异常盘口 买1：{}   卖1：{} 最新成交： {}".format(bids[0], asks[0], latest_trade[0]['price']))

        simple_log.write(note_simple)
        detail_log.write(note_detail)

        simple_log.flush()
        detail_log.flush()


if __name__ == '__main__':
    """
    ct = CoinTiger(*load_api_key('cointiger'))
    while True:
        try:
            ct.check_order_book('kkgeth')
            time.sleep(30)
        except Exception as e:
            print("fail all", e)

    """

    ctws = CoinTigerWS('kkgeth')
    while True:
        ctws.ws.run_forever()
        print("websocket disconnect", datetime.datetime.now())
        time.sleep(3)

    """
    ct = CoinTiger(*load_api_key('cointiger'))
    order_list = []
    for order_id in [3363]:#[3362, 3361, 3364, 3363, 3387, 3386, 3420, 3419]:
        try:
            t = time.time()
            print(ct.get_match_detail('kkgeth', order_id))
            take_time = time.time() - t
        except:
            break
        time.sleep(max(0.05, 0.2 - take_time))
        print(order_id)
    """
