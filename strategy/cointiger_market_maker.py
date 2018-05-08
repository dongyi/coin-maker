import random
import time

from lib.util import *
from exchange.cointiger import CoinTiger




class Bots:
    def __init__(self, base_coin, target_coin, capital_password):
        self.base_coin = base_coin
        self.target_coin = target_coin
        self.capital_password = capital_password
        self.trade_pair = '{}{}'.format(target_coin, base_coin)
        self.api_client = CoinTiger(*load_api_key('cointiger'))

    def strategy_ctrl(self):
        pass

    def test(self, test_type):
        if test_type == 'order_and_cancel':
            order_id = self.api_client.order(side='BUY', order_type=1, volume=0.1,
                    capital_password=self.capital_password, price=0.01,
                    symbol='eoseth')
            print(order_id)
            time.sleep(2)

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

    def run(self):
        while True:
            """
            query current status
            
            place order on bid1 ask1
            
            query last order status
            
            if success then sleep and wait next loop
            if fail then cancel orders and wait next loop
            
            """
            print(self.base_coin, self.api_client.get_balance(self.base_coin))
            print(self.target_coin, self.api_client.get_balance(self.target_coin))

            time.sleep(10)
