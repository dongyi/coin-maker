import requests
import json
import time
import dateutil
import pandas as pd
import numpy as np


from utils import retry_call

base_url = "http://data.bter.com"
interval = 10


@retry_call(5)
def get_match_record(pair):
    url = "{}/api2/1/tradeHistory/{}".format(base_url, pair)

    res = json.loads(requests.get(url).text)
    return res['data']


def dump_file(record_list, pair):
    file = 'trade-log-{}'.format(pair)
    txt = '\n'.join([json.dumps(i) for i in record_list])
    with open(file, 'a') as f:
        f.write(txt)
        f.write('\n')


def collect_trades(pair):
    current_trade_id = 0

    while True:
        try:
            new_trades = get_match_record(pair)
        except:
            time.sleep(10)
            continue

        latest_trades = [i for i in new_trades if int(i['tradeID']) > current_trade_id]
        dump_file(latest_trades, pair)

        current_trade_id = max([int(i['tradeID']) for i in new_trades])

        time.sleep(interval)


