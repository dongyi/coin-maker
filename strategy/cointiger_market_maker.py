import random
import time


from lib.util import *
from exchange.cointiger import CoinTiger

ct = CoinTiger(*load_api_key('cointiger'))


def strategy_ctrl():
    pass

def strategy_init():
    pass

def run():
    while True:
        """
        query current status
        
        place order on bid1 ask1
        
        query last order status
        
        if success then sleep and wait next loop
        if fail then cancel orders and wait next loop
        
        """
        print('eth:', ct.get_balance('eth'))
        print('eos:', ct.get_balance('eos'))
        time.sleep(10)