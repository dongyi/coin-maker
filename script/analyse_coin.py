import requests
import pandas as pd
import numpy as np
import json
# import seaborn

import datetime
#import talib
#import scipy.stats

from functools import lru_cache
from itertools import combinations


def get_coin_list(limit=20):
    url = "https://s2.coinmarketcap.com/generated/search/quick_search.json"
    struct = json.loads(requests.get(url).text)
    coin_list = [i['slug'] for i in struct[:limit]]
    return coin_list


@lru_cache(2 ** 32)
def get_price(coin_name):
    url = "https://graphs2.coinmarketcap.com/currencies/{}/1504115174203/1517904841000/".format(coin_name)

    print(url)
    body = requests.get(url).text
    struct = json.loads(body)
    price_series = pd.DataFrame(
        [{'price': i[1], 'date': datetime.datetime.fromtimestamp(i[0] / 1000)} for i in struct['price_usd']])
    return price_series


def get_total_df():
    coin_list = ['bitcoin', 'ethereum', 'ethereum-classic', 'golem-network-tokens', 'zcash',
                 'bitshares', 'digixdao', 'siacoin', 'firstblood', 'ripple', 'neo', 'litecoin', 'dash', 'monero']
    df_list = []
    for c in coin_list:
        print("fetch {}".format(c))
        price_usd = get_price(c)
        df_list.append(pd.DataFrame(price_usd))
    total = pd.concat(df_list, axis=1)
    total.to_csv('total_crypto.csv')





def compute_all():
    dimension = 20
    # coin_list = get_coin_list(dimension)
    coin_list = ['bitcoin', 'ethereum', 'ethereum-classic', 'golem-network-tokens', 'zcash',
                 'bitshares', 'digixdao', 'siacoin', 'firstblood']
    df = pd.DataFrame(index=coin_list, columns=coin_list)

    for combine in combinations(coin_list, 2):
        print("compute {}".format(combine))
        price_a = get_price(combine[0]).set_index('date').resample('1d').mean()[-60:].pct_change()
        price_b = get_price(combine[1]).set_index('date').resample('1d').mean()[-60:].pct_change()
        merged_df = pd.concat([price_a, price_b], axis=1).dropna()
        merged_df.columns = ['price_a', 'price_b']
        coefficient, p = scipy.stats.pearsonr(merged_df['price_a'], merged_df['price_b'])
        df.loc[combine[0], combine[1]] = coefficient
        df.loc[combine[1], combine[0]] = coefficient
        print(coefficient, p)

    df.to_csv('analyse_2.csv')
    # plot in notebook
    # seaborn.heatmap(df)


if __name__ == '__main__':
    get_total_df()
    # print(cl)
