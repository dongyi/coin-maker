import pandas as pd

from lib.util import load_api_key
from lib.util import retry_call

from exchange.bittrex import Bittrex


def get_volatility_df(exchange):
    pair_list = ['USDT-BTC', 'BTC-1ST', 'BTC-ETH', 'BTC-OMG', 'BTC-GNT', 'BTC-XRP', 'BTC-SC', 'BTC-DASH', 'BTC-QTUM', 'BTC-SNT']

    bittrex_api = Bittrex(*load_api_key(exchange))

    for pair in pair_list:
        hist = pd.DataFrame(bittrex_api.getHistoricalData(market=pair, period=100, unit='day'))
        hist['H'] = hist['H'] / hist['C'].mean()
        hist['L'] = hist['L'] / hist['C'].mean()

        hist['v'] = hist['H'] / hist['L']

        print("volatility of {} is {}".format(pair, hist['v'].std()))
