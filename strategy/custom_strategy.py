from concurrent import futures

from lib.util import load_api_key
from lib.util import fail_default
from lib.util import retry_call
from lib.util import red, green


from exchange.bittrex import Bittrex

import datetime
import dateutil.parser
import time
import talib
import pandas as pd
import numpy as np

latest_btc = 0


@fail_default('error in fetch price')
def find_breakout_and_trade(p, exchange):
    df_vol = pd.DataFrame([])
    global latest_btc
    while True:
        my_bittrex = Bittrex(*load_api_key(exchange))
        closing_prices_1min = my_bittrex.getClosingPrices(p, 100, 'fiveMin')
        df = pd.DataFrame([])
        df['close'] = closing_prices_1min
        df['ma5'] = df['close'].rolling(5).mean().fillna(method='bfill')
        df['diff'] = df['close'] - df['ma5']
        df['higher'] = df['diff'].apply(lambda x: x > 0)
        cpx = df['close'].tolist()[-1]
        if p == 'USDT-BTC':
            latest_btc = cpx
            cny_price = cpx * 6.5
        else:
            cny_price = cpx * latest_btc * 6.5
        if df['higher'].tail(5).tolist()[::-1] == [False, False, False, False, True]:

            print(green("{} breakout up at price {}".format(p, cny_price)))
        if df['higher'].tail(5).tolist()[::-1] == [True, True, True, True, False]:
            print(red("{} breakout down at price {}".format(p, cny_price)))

        order_slice = my_bittrex.get_market_history(p, 100)

        slice_df = pd.DataFrame(order_slice['result'])

        df_vol = df_vol.append(slice_df)
        df_vol.drop_duplicates(subset=['Id'], keep='last', inplace=True)

        now = datetime.datetime.now()

        near_vol = df_vol[df_vol['TimeStamp'].apply(lambda x: (now - dateutil.parser.parse(x)).seconds < 300 + 8*3600)].copy()
        far_vol = df_vol[df_vol['TimeStamp'].apply(lambda x: (now - dateutil.parser.parse(x)).seconds < 3000 + 8*3600)].copy()

        if near_vol['Quantity'].mean() > far_vol['Quantity'].mean() * 2:
            print(green("high volume {}, {}".format(p, near_vol['Quantity'].mean())))

        time.sleep(10)


def runner(exchange):
    pairs = ['USDT-BTC', 'BTC-1ST', 'BTC-ETH', 'BTC-OMG', 'BTC-GNT', 'BTC-BCC', 'BTC-SC']

    with futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_pair = dict((executor.submit(find_breakout_and_trade, p, exchange), p)
                              for p in pairs)

        for future in futures.as_completed(future_to_pair):
            p = future_to_pair[future]
            if future.exception() is not None:
                print('{} generated an exception: {}'.format(p, future.exception()))
            else:
                print('{} result: {}'.format(p, future.result()))
