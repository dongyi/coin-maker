from lib.util import fail_default
from lib.util import red, green

from exchange.data_proxy import DataProxy

import datetime
import dateutil.parser
import time
import pandas as pd
import gevent

from settings import exchange_rate

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

    global latest_btc
    while True:
        now_dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_api = DataProxy(exchange)
        ohlc = data_api.ohlc(p, 100, 'oneMin')
        closing_prices_1min = [i['close'] for i in ohlc]
        df = pd.DataFrame([])
        df['close'] = closing_prices_1min
        df['ma5'] = df['close'].rolling(5, center=False).mean().fillna(method='bfill')
        df['diff'] = df['close'] - df['ma5']
        df['higher'] = df['diff'].apply(lambda x: x > 0)
        cpx = df['close'].tolist()[-1]
        if p == 'USDT-BTC':
            latest_btc = cpx
            cny_price = cpx * exchange_rate['cny']
        else:
            cny_price = cpx * latest_btc * exchange_rate['cny']
        if df['higher'].tail(5).tolist()[::-1] == [True, False, False, False, False]:
            print(green("[{}] {} breakout up at price {}, fiat price: {}".format(now_dt, p, cpx, cny_price)))
        if df['higher'].tail(5).tolist()[::-1] == [False, True, True, True, True]:
            print(red("[{}] {} breakout down at price {}, fiat price: {}".format(now_dt, p, cpx, cny_price)))

        ohlc_df = pd.DataFrame(ohlc)
        ohlc_df['local_tm'] = ohlc_df['timestamp'].apply(lambda x: dateutil.parser.parse(x) + datetime.timedelta(hours=8))
        now = datetime.datetime.now()

        near_vol = ohlc_df[ohlc_df['local_tm'].apply(lambda x:(now - x).seconds < 60)].copy()
        far_vol = ohlc_df[ohlc_df['local_tm'].apply(lambda x:(now - x).seconds < 3600)].copy()

        if near_vol['volume'].mean() > far_vol['volume'].mean() * 2:
            print(green("[{}] high volume {}, {}".format(now_dt, p, near_vol['volume'].mean())))
        time.sleep(30)


def runner(exchange):
    pairs = ['USDT-BTC', 'BTC-1ST', 'BTC-ETH', 'BTC-OMG', 'BTC-GNT', 'BTC-BCC', 'BTC-SC']
    l = []
    for p in pairs:
        l.append(gevent.spawn(find_breakout_and_trade, p, exchange))

    gevent.joinall(l)
