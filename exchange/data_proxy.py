from lib.util import load_api_key
from lib.util import retry_call

from exchange.bigone import Client as Bigone
from exchange.binance import BinanceAPI as Binance
from exchange.bittrex import Bittrex

from exchange.okex import OKCoinSpot as Okex
from exchange.hitbtc import Hitbtc
from exchange.poloniex import Poloniex
from exchange.bitstamp import Bitstamp


class DataProxy:

    def __init__(self, exchange):
        self.__exchange = exchange
        self.__api_class = {
            'bigone': Bigone,
            'binance': Binance,
            'bittrex': Bittrex,
            'okex': Okex,
            'hitbtc': Hitbtc,
            'poloniex': Poloniex,
            'bitstamp': Bitstamp,
        }[exchange]
        self.__api_client = self.__api_class(*load_api_key(exchange))

    @retry_call(3)
    def ohlc(self, pair, period, unit):
        pass

    @retry_call(3)
    def trades(self):
        pass

    @retry_call(3)
    def order_books(self):
        pass
