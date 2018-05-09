import random
import time
import numpy as np
import pandas as pd
import datetime

from lib.persist import get_db_engine
from lib.persist import sql_to_df
from lib.util import *
from exchange.cointiger import CoinTiger


class Bots:
    def __init__(self, base_coin, target_coin, capital_password, trader_id,
                 interval_max=60 * 2, interval_min=20, vol_max=0.002, vol_min=0.001):
        self.base_coin = base_coin
        self.target_coin = target_coin
        self.capital_password = capital_password
        self.trade_pair = '{}{}'.format(target_coin, base_coin)
        self.api_client = CoinTiger(*load_api_key('cointiger'))
        self.interval_max = interval_max
        self.interval_min = interval_min
        self.vol_max = vol_max
        self.vol_min = vol_min
        self.trader_id = trader_id
        self.status = 'halt'

    def strategy_ctrl(self, cmd):
        if cmd == 'start':
            self.set_status('run')
            self.run()
        elif cmd == 'pause':
            self.set_status('suspend')
        elif cmd == 'stop':
            self.set_status('halt')
        else:
            raise Exception("no such cmd")

    def set_status(self, new_status):
        assert new_status in ['halt', 'suspend', 'run']
        self.status = new_status

    def get_status(self):
        return self.status

    def test(self, test_type='order_and_cancel'):
        if test_type == 'order_and_cancel':
            order_ret = self.api_client.order(side='BUY', order_type=1, volume=0.1,
                                              capital_password=self.capital_password, price=0.01,
                                              symbol=self.trade_pair)
            order_id = order_ret['data']['order_id']
            self.api_client.cancel_order(order_id, self.trade_pair)
            print(self.api_client.get_order_trade(self.trade_pair, offset=1, limit=10))
            """
            {'offset': 0, 'limit': 10, 'count': 1, 'list':
            [
                {
                'volume': {'amount': '0.100', 'icon': '', 'title': 'volume'},
                'side': 'BUY',
                'price': {'amount': '0.01000000', 'icon': '', 'title': 'price'},
                'created_at': 1525743503331,
                'id': 6054848,
                'label': {'title': 'Cancel', 'click': 1},
                'remain_volume': {'amount': '0.10000000', 'icon': '', 'title': 'Remain volume'},
                'side_msg': 'Buy'}]}
            """
        if test_type == 'orderbook':
            orderbook_list = self.api_client.get_orderbook(self.trade_pair)
            bid_price1, bid_vol1 = orderbook_list['depth_data']['tick']['buys'][0]
            ask_price1, ask_vol1 = orderbook_list['depth_data']['tick']['asks'][0]

        if test_type == 'order_history':
            self.sync_trade_history()

        if test_type == 'get_order_history':
            res = self.api_client.get_order_history('eoseth', 1, 20)
            print(res)

    def sync_trade_history(self):

        current_max_order_id = \
            sql_to_df('select max(order_id) from trade_record where trader_id={}'.format(self.trader_id)).iloc[0, 0]

        batch_limit = 10
        offset = 1
        df = pd.DataFrame([])
        while True:
            trade_history = self.api_client.get_trade_history(self.trade_pair, offset, batch_limit)
            if len(trade_history['list']) == 0:
                break
            df = df.append(pd.DataFrame(trade_history['list']))
            offset += batch_limit
        for to_fix in ['deal_price', 'price', 'volume']:
            df[to_fix] = df[to_fix].apply(lambda x: x['amount'])
        df['trader_id'] = self.trader_id
        df['base_coin'] = self.base_coin
        df['target_coin'] = self.target_coin
        df.rename(columns={"created_at": "timestamp", "id": "order_id"}, inplace=True)
        df['timestamp'] = df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x / 1000))

        df = df[df['order_id'] > current_max_order_id]
        if len(df) > 0:
            df.to_sql('trade_record', con=get_db_engine(), if_exists='append', index=False)

    def notify(self, msg):
        pass

    def record_order(self, content_obj, record_type):
        """{
            'side': trade_side,
            'base': self.base_coin,
            'target': self.target_coin,
            'price': my_price,
            'volume': current_loop_fund,
            'ts': int(time.time()),
            'trader_id': self.trader_id
        }"""
        if record_type == 'exception':
            df = pd.DataFrame([content_obj])
            df.to_sql('trade_exception', con=get_db_engine(), if_exists='append', index=False)
        if record_type == 'success':
            pass
        print("record order:", content_obj)

    def run(self):
        while True:
            if self.status == 'halt':
                break
            if self.status == 'suspend':
                time.sleep(1)
                continue
            current_loop_fund_percetage = random.random() / 10
            current_loop_fund = self.vol_min + (self.vol_max - self.vol_min) * current_loop_fund_percetage
            sleep_interval = random.randint(self.interval_min, self.interval_max)

            current_base_coin_balance = float(self.api_client.get_balance(self.base_coin)[0]['normal'])
            current_target_coin_balance = float(self.api_client.get_balance(self.target_coin)[0]['normal'])

            print(self.base_coin, current_base_coin_balance)
            print(self.target_coin, current_target_coin_balance)

            # check balance
            if current_base_coin_balance < current_loop_fund:
                self.notify('{} not enough'.format(self.base_coin))
                time.sleep(60)
                continue

            # cancel all unfilled orders
            current_open_orders = self.api_client.get_order_trade(self.trade_pair, 1, 10)
            if current_open_orders['count'] > 0:
                remain_open_orders = current_open_orders['list']
                for open_order in remain_open_orders:
                    self.api_client.cancel_order(order_id=open_order['id'], symbol=self.trade_pair)

            # use mean value of bid1 and ask1 as order price
            orderbook_list = self.api_client.get_orderbook(self.trade_pair)
            bid_price1, bid_vol1 = orderbook_list['depth_data']['tick']['buys'][0]
            ask_price1, ask_vol1 = orderbook_list['depth_data']['tick']['asks'][0]
            bid_price1 = float(bid_price1)
            ask_price1 = float(ask_price1)

            price_range_percetage = random.random()
            my_price = (ask_price1 - bid_price1) * price_range_percetage + bid_price1

            # place buy and sell orders
            buy_order_ret = self.api_client.order(side='BUY', order_type=1,
                                                  volume=current_base_coin_balance * current_loop_fund_percetage / my_price,
                                                  capital_password=self.capital_password, price=my_price,
                                                  symbol=self.trade_pair)

            sell_order_ret = self.api_client.order(side='SELL', order_type=1,
                                                   volume=current_base_coin_balance * current_loop_fund_percetage / my_price,
                                                   capital_password=self.capital_password, price=my_price,
                                                   symbol=self.trade_pair)

            time.sleep(1)

            if not (buy_order_ret['code'] == '0' and sell_order_ret['code'] == '0'):
                # fail one or two
                if buy_order_ret['code'] == '0' and sell_order_ret['code'] != '0':
                    print("sell order remains")
                    buy_order_id = buy_order_ret['data']['order_id']
                    self.api_client.cancel_order(buy_order_id, self.trade_pair)
                    time.sleep(sleep_interval)
                    continue
                if buy_order_ret['code'] != '0' and sell_order_ret['code'] == '0':
                    print("buy order remains")
                    sell_order_id = sell_order_ret['data']['order_id']
                    self.api_client.cancel_order(sell_order_id, self.trade_pair)
                    time.sleep(sleep_interval)
                    continue
                else:
                    # fail both
                    print("both order failed")
                    time.sleep(sleep_interval)
                    continue
            else:
                buy_order_id = buy_order_ret['data']['order_id']
                sell_order_id = sell_order_ret['data']['order_id']

                print("buy order: {} sell order: {}".format(buy_order_id, sell_order_id))

            # check remain orders
            current_open_orders = self.api_client.get_order_trade(self.trade_pair, 1, 20)
            if current_open_orders['count'] > 0:
                remain_open_orders = current_open_orders['list']
                for open_order in remain_open_orders:
                    order_id = open_order['id']
                    remain_volume = float(open_order['remain_volume']['amount'])
                    assert order_id in [buy_order_id, sell_order_id]
                    trade_side = 'BUY' if order_id == sell_order_id else 'SELL'
                    record_obj = {
                        'order_id': order_id,
                        'side': trade_side,
                        'base_coin': self.base_coin,
                        'target_coin': self.target_coin,
                        'price': my_price,
                        'volume': current_loop_fund - remain_volume,
                        'timestamp': datetime.datetime.fromtimestamp(time.time()),
                        'trader_id': self.trader_id
                    }
                    self.record_order(record_obj, 'exception')
                    self.api_client.cancel_order(order_id=open_order['id'], symbol=self.trade_pair)
            else:
                price = my_price
                volume = current_base_coin_balance * current_loop_fund_percetage / my_price
                record_obj_list = [{
                    'trader_id': self.trader_id,
                    'base_coin': self.base_coin,
                    'target_coin': self.target_coin,
                    'order_id': buy_order_id,
                    'side': 'buy',
                    'deal_price': price * volume,
                    'timestamp': datetime.datetime.now(),
                    'volume': volume,
                    'price': price,
                }, {
                    'trader_id': self.trader_id,
                    'base_coin': self.base_coin,
                    'target_coin': self.target_coin,
                    'order_id': sell_order_id,
                    'side': 'sell',
                    'deal_price': price * volume,
                    'timestamp': datetime.datetime.now(),
                    'volume': volume,
                    'price': price,
                }
                ]
                df = pd.DataFrame(record_obj_list)
                df.to_sql('trade_record_realtime', con=get_db_engine(), if_exists='append', index=False)
            # sleep till next loop
            print("next loop in ", sleep_interval)
            time.sleep(sleep_interval)
