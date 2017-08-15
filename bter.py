import requests
import json
import time
import dateutil
import pandas as pd
import numpy as np
import seaborn

from utils import retry_call

base_url = "http://data.bter.com"
interval = 10


@retry_call(5)
def get_match_record(pair, tid=0):
    url = "{}/api2/1/tradeHistory/{}".format(base_url, pair)

    if tid > 0:
        url += '/{}'.format(tid)

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


def collect_trades_history(pair):
    current_trade_id = 0
    total_res = []

    while True:
        try:
            new_trades = get_match_record(pair, current_trade_id)
        except:
            continue

        latest_trades = [i for i in new_trades if int(i['tradeID']) > current_trade_id]

        current_trade_id = min([int(i['tradeID']) for i in new_trades])
        total_res.extend(latest_trades)
        if len(total_res) > 100000:
            break
    return pd.DataFrame(total_res)


def load_file(pair):
    """
    {
        tradeID: "23624916",
        date: "2017-08-14 03:04:50",
        type: "sell",
        rate: 2062.1,
        amount: 3.3089,
        total: 6823.28269
    },
    :param pair: 
    :return: 
    """
    file = 'trade-log-{}'.format(pair)
    content = open(file, 'a').read()
    record_list = [json.loads(i) for i in content.split('\n') if i.strip() != '']
    df = pd.DataFrame(record_list)
    df['pure'] = df['type'].apply(lambda x: 1 if x == 'buy' else -1) * df['total']
    df['pure_sum'] = df['pure'].cumsum()
    return df
