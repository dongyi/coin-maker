import requests
import pandas as pd
import numpy as np
import json
import seaborn

import talib
import scipy.stats

from functools import lru_cache

def get_coin_list(limit=20):
    url = "https://files.coinmarketcap.com/generated/search/quick_search.json"
    struct = json.loads(requests.get(url).text)
    coin_list = [i['token'][0] for i in struct[:20]]
    return coin_list

@lru_cache(2**32)
def get_price(coin_name):
    url = "https://graphs.coinmarketcap.com/currencies/{}".format(coin_name)
    struct = json.loads(requests.get(url).text)
    price_series = np.array([i[1] for i in srtuct['price_usd']])
    return price_series

def compute_all():
    dimension = 20
    coin_list = get_coin_list(dimension)
    df = pd.DataFrame(index=coin_list, column=coin_list)
    for idx_i in range(dimension):
        for idx_j in range(idx_i, dimension):
            coin_a = coin_list[idx_i]
            coin_b = coin_list[idx_j]
            
            coefficient, p = scipy.stats.pearsonr(get_price(coin_a), get_price(coin_b))
            print(coefficient, coin_a, coin_b)
            #df.iloc[idx_i, idx_j] = coefficient
    df.to_csv('analyse.csv')
    # plot in notebook
    #seaborn.heatmap(df)

if __name__ == '__main__':
    compute_all()
