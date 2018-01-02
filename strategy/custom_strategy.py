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
import gevent
from functools import partial

latest_btc = 0
from gevent import monkey

monkey.patch_time()
monkey.patch_socket()
monkey.patch_signal()
monkey.patch_os()

monkey.patch_dns()
monkey.patch_sys()


@fail_default('error in fetch price')
def find_breakout_and_trade(p, exchange):
    df_vol = pd.DataFrame([])
    print("start....", p)
    while True:
        now_dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        my_bittrex = Bittrex(*load_api_key(exchange))
        closing_prices_1min = my_bittrex.getClosingPrices(p, 100, 'fiveMin')
        df = pd.DataFrame([])
        df['close'] = closing_prices_1min
        df['ma5'] = df['close'].rolling(5, center=False).mean().fillna(method='bfill')
        df['diff'] = df['close'] - df['ma5']
        df['higher'] = df['diff'].apply(lambda x: x > 0)
        cpx = df['close'].tolist()[-1]
        if p == 'USDT-BTC':
            latest_btc = cpx
            cny_price = cpx * 6.5
        else:
            cny_price = cpx * latest_btc * 6.5
        if df['higher'].tail(5).tolist()[::-1] == [True, False, False, False, False]:
            print(green("[{}] {} breakout up at price {}".format(now_dt, p, cny_price)))
        if df['higher'].tail(5).tolist()[::-1] == [False, True, True, True, True]:
            print(red("[{}] {} breakout down at price {}".format(now_dt, p, cny_price)))

        order_slice = my_bittrex.get_market_history(p, 100)

        slice_df = pd.DataFrame(order_slice['result'])

        df_vol = df_vol.append(slice_df)
        df_vol.drop_duplicates(subset=['Id'], keep='last', inplace=True)

        now = datetime.datetime.now()

        near_vol = df_vol[df_vol['TimeStamp'].apply(lambda x: (now - dateutil.parser.parse(x)).seconds < 300 + 8*3600)].copy()
        far_vol = df_vol[df_vol['TimeStamp'].apply(lambda x: (now - dateutil.parser.parse(x)).seconds < 3000 + 8*3600)].copy()

        if near_vol['Quantity'].mean() > far_vol['Quantity'].mean() * 2:
            print(green("[{}] high volume {}, {}".format(now_dt, p, near_vol['Quantity'].mean())))
        time.sleep(10)


def runner(exchange):
    pairs = ['USDT-BTC', 'BTC-1ST', 'BTC-ETH', 'BTC-OMG', 'BTC-GNT', 'BTC-BCC', 'BTC-SC']
    l = []
    for p in pairs:
        l.append(gevent.spawn(find_breakout_and_trade, p, exchange))

    gevent.joinall(l)
