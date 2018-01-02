"""

price break ma5 smoothly, send notification

"""

import time
import talib
import pandas as pd
import numpy as np

from concurrent import futures

from lib.util import load_api_key
from lib.util import fail_default
from lib.util import red, green

from exchange.bittrex import Bittrex


@fail_default('error in fetch price')
def find_breakout(p):
    while True:
        my_bittrex = Bittrex(*load_api_key('bittrex'))
        closing_prices_1min = my_bittrex.getClosingPrices(p, 100, 'oneMin')
        df = pd.DataFrame([])
        df['close'] = closing_prices_1min
        df['ma5'] = df['close'].rolling(5).mean().fillna(method='bfill')
        df['diff'] = df['close'] - df['ma5']
        df['higher'] = df['diff'].apply(lambda x: x > 0)
        cpx = df['close'].tolist()[-1]
        if df['higher'].tail(5).tolist() == [False, False, False, False, True]:
            print(green("{} breakout up at price {}".format(p, cpx)))
        if df['higher'].tail(5).tolist() == [True, True, True, True, False]:
            print(red("{} breakout down at price {}".format(p, cpx)))
        print("{} hodl current price: {}".format(p, cpx))
        time.sleep(10)


@fail_default('error in fetch price')
def break_bollinger_bands(p, exchange):
    while True:
        my_bittrex = Bittrex(*load_api_key(exchange))
        closing_prices_1min = my_bittrex.getClosingPrices(p, 100, 'fiveMin')
        cpx = closing_prices_1min[-1]

        pct_change = closing_prices_1min[-1] / closing_prices_1min[-2]
        upper, middle, lower = talib.BBANDS(np.asarray(closing_prices_1min),
                                            timeperiod=15, nbdevup=1, nbdevdn=1, matype=0)

        upper = upper[-1]
        lower = lower[-1]
        if cpx < lower and pct_change > 0.97:
            # break bollinger bands up
            print(green("{} breakout up at price {}".format(p, cpx)))

        elif cpx > upper or pct_change < 0.97:
            # break bollinger bands down
            print(red("{} breakout down at price {}".format(p, cpx)))
        time.sleep(10)
        print("\n")


def runner(exchange):
    pairs = ['USDT-BTC', 'BTC-1ST', 'BTC-ETH', 'BTC-OMG', 'BTC-GNT', 'BTC-BCC', 'BTC-SC']

    with futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_pair = dict((executor.submit(break_bollinger_bands, p, exchange), p)
                              for p in pairs)

        for future in futures.as_completed(future_to_pair):
            p = future_to_pair[future]
            if future.exception() is not None:
                print('{} generated an exception: {}'.format(p,
                                                             future.exception()))
            else:
                print('{} result: {}'.format(p, future.result()))
