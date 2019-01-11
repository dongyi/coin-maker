import time
import json
import gevent
import requests


from exchange.cointiger import CoinTiger as ExchangeAPI


INTERVAL = 2
API_KEY = ''
API_SECRET = ''


class Watcher:
    # find arbitrage chances
    def __init__(self):
        self.api_client = ExchangeAPI(API_KEY, API_SECRET)
        self.trading_pairs = self.api_client.get_all_trading_pairs()

    def single_loop(self):
        # find out all trading pairs
        pass

    def run(self):
        while True:
            self.single_loop()
            time.sleep(INTERVAL)


class Bot:

    def __init__(self):
        self.api_client = ExchangeAPI(API_KEY, API_SECRET)

    def single_loop(self):

        # step one: check open orders

        # step two: cancel all open orders

        # step three: check arbitrage chances

        # place orders

        pass

    def run(self):
        while True:
            self.single_loop()
            time.sleep(INTERVAL)


if __name__ == '__main__':
    bot = Bot()
    watcher = Watcher()

    gevent.joinall([bot.run(), watcher.run()])
