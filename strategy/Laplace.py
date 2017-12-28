"""
 indicator: (bidSize * bidPrice - askSize * askPrice) / (bidSize * bidPrice + askSize * askPrice)
"""

from exchange.bittrex import Bittrex
from lib.util import load_api_key

import pandas as pd


def laplace_indicator(pair, exchange):
    bittrex_api = Bittrex(*load_api_key(exchange))

    full_order_book = bittrex_api.get_orderbook(pair, 'both', 20)

    assert full_order_book['success'] is True

    df_buy = pd.DataFrame(full_order_book['result']['buy'])
    df_sell = pd.DataFrame(full_order_book['result']['sell'])

    bid_sum = df_buy['Quantity'] * df_buy['Rate']
    ask_sum = df_sell['Quantity'] * df_sell['Rate']

    laplace_value = (bid_sum.sum() - ask_sum.sum()) / (bid_sum.sum() + ask_sum.sum())
    return laplace_value