import requests
import json
import time

import pandas as pd
import numpy as np


from utils import retry_call

base_url = "http://data.bter.com"


@retry_call(5)
def get_match_record(pair):
    url = "{}/api2/1/tradeHistory/{}".format(base_url, pair)

    res = json.loads(requests.get(url).text)
    return res['data']


def collect_trades(pair):
    current_trade_id = 0

    while True:
        new_trades = get_match_record(pair)

        latest_trades = [i for i in new_trades if int(i['tradeID']) > current_trade_id]

        current_trade_id = max([int(i['tradeID']) for i in new_trades])

        time.sleep(10)
