from exchange.bittrex import Bittrex
from lib.util import load_api_key
from lib.util import retry_call

import pandas as pd
import numpy as np
import time


@retry_call(3)
def collector(exchange, market):
    """
    {
	"success" : true,
	"message" : "",
	"result" : [{
			"Id" : 319435,
			"TimeStamp" : "2014-07-09T03:21:20.08",
			"Quantity" : 0.30802438,
			"Price" : 0.01263400,
			"Total" : 0.00389158,
			"FillType" : "FILL",
			"OrderType" : "BUY"
		}, {
			"Id" : 319433,
			"TimeStamp" : "2014-07-09T03:21:20.08",
			"Quantity" : 0.31820814,
			"Price" : 0.01262800,
			"Total" : 0.00401833,
			"FillType" : "PARTIAL_FILL",
			"OrderType" : "BUY"
    :param exchange: 
    :param market: 
    :return: 
    """
    api_key, secret_key = load_api_key(exchange)
    bittrex = Bittrex(api_key, secret_key)
    order_slice = bittrex.get_market_history(market, 100)

    return order_slice


def runner(exchange, market):
    df = pd.DataFrame([])
    counter = 0
    while True:
        slice = collector(exchange, market)
        slice_df = pd.DataFrame(slice['result'])

        df = df.append(slice_df)
        df.drop_duplicates(subset=['Id'], keep='last', inplace=True)
        print("collected from {} to {}".format(min(df['Id'].tolist()), max(df['Id'].tolist())))
        time.sleep(15)
        counter += 1
        if counter % 10 == 0:
            df.to_csv('orders_{}_{}.csv'.format(exchange, market))


if __name__ == '__main__':
    import sys
    sys.path.append('../')
    runner('bittrex', '1ST-BTC')
