"""

price break ma5 smoothly, send notification

"""

import time
import pandas as pd

from concurrent import futures
from lib.util import load_api_key
from lib.util import retry_call
from lib.util import fail_silent
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
            print(red('{} breakout at price {}'.format(p, cpx)))
        print("{} hodl current price: {}".format(p, cpx))
        time.sleep(10)


def runner():
    pairs = ['USDT-BTC', 'BTC-1ST', 'BTC-ETH', 'BTC-OMG', 'BTC-GNT', 'BTC-BCC', 'BTC-SC']

    with futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_pair = dict((executor.submit(find_breakout, p), p)
                              for p in pairs)

        for future in futures.as_completed(future_to_pair):
            p = future_to_pair[future]
            if future.exception() is not None:
                print('{} generated an exception: {}'.format(p,
                                                             future.exception()))
            else:
                print('{} result: {}'.format(p, future.result()))
