import os

import pandas as pd
import numpy as np
import talib
import pickle


def load_history(market):
    file_path = 'persist/{}'.format(market)
    df = pd.DataFrame.from_csv(os.path.join(file_path, 'hist.csv'), encoding='utf8')
    return df


def dump_history(market, df):
    file_path = 'persist/{}'.format(market)
    df.to_csv(os.path.join(file_path, 'hist.csv'), encoding='utf8')


def add_fator(df):
    df['macd'] = talib.MACD(df['close'].as_matrix())

    df['rsi_6'] = talib.RSI(df['close'].values, 6)
    df['rsi_12'] = talib.RSI(df['close'].values, 12)
    df['rsi_18'] = talib.RSI(df['close'].values, 18)

    ks, ds = talib.STOCH(high=df['high'].values,
                         low=df['low'].values,
                         close=df['close'].values)

    js = 3 * ks - 2 * ds

    k, d, j = ks[-1], ds[-1], js[-1]
    df['k'] = k
    df['d'] = d
    df['j'] = j

    return df
