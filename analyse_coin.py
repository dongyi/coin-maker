import requests
import pandas as pd
import numpy as np
import json
#import seaborn

import datetime
import talib
import scipy.stats

from functools import lru_cache
from itertools import combinations


def get_coin_list(limit=20):
    url = "https://files.coinmarketcap.com/generated/search/quick_search.json"
    struct = json.loads(requests.get(url).text)
    coin_list = [i['slug'] for i in struct[:20]]
    return coin_list

@lru_cache(2**32)
def get_price(coin_name):
    url = "https://graphs.coinmarketcap.com/currencies/{}".format(coin_name)
    body = requests.get(url).text
    struct = json.loads(body)
    price_series = pd.DataFrame([{'price': i[1], 'date': datetime.datetime.fromtimestamp(i[0]/1000)} for i in struct['price_usd']])
    return price_series

def compute_all():
    dimension = 20
    coin_list = get_coin_list(dimension)
    df = pd.DataFrame(index=coin_list, columns=coin_list)

    for combine in combinations(coin_list, 2):
        print("compute {}".format(combine))
        price_a = get_price(combine[0]).set_index('date').resample('1d').mean()
        price_b = get_price(combine[1]).set_index('date').resample('1d').mean()
        merged_df = pd.concat([price_a, price_b], axis=1).dropna()
        merged_df.columns = ['price_a', 'price_b']
        coefficient, p = scipy.stats.pearsonr(merged_df['price_a'], merged_df['price_b'])
        df.loc[combine[0], combine[1]] = coefficient
        df.loc[combine[1], combine[0]] = coefficient
        print(coefficient, p)

    df.to_csv('analyse.csv')
    # plot in notebook
    #seaborn.heatmap(df)

if __name__ == '__main__':
    compute_all()
