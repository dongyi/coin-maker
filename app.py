import json

from lib.util import *
#from twilio.rest import Client
from ta.indicators import *

from exchange.bittrex import Bittrex
from exchange.bittrex import getClosingPrices

# Creating an instance of the Bittrex class with our secrets.json file
with open("secrets.json") as secrets_file:
    secrets = json.load(secrets_file)
    secrets_file.close()
    my_bittrex = Bittrex(secrets['bittrex_key'], secrets['bittrex_secret'])

# Setting up Twilio for SMS alerts

#account_sid = secrets['twilio_key']
#auth_token = secrets['twilio_secret']
#client = Client(account_sid, auth_token)


coin_pairs = ['USDT-BTC', 'BTC-1ST', 'BTC-ETH', 'BTC-OMG', 'BTC-GNT', 'BTC-BCC', 'BTC-NEO']


if __name__ == "__main__":

    print("===============================================================================")
    print("\t\t\t bittrex indicator")
    print("===============================================================================")


    def get_signal():
        current_btc_usd = 0.0
        cny_usd = 6.56

        for i in coin_pairs:
            closing_prices_5min = getClosingPrices(my_bittrex, i, 100, 'fiveMin')
            closing_prices_30min = getClosingPrices(my_bittrex, i, 100, 'thirtyMin')

            signal = 'breakout:' + findBreakout(closing_prices_5min, 30)
            rsi = calculateRSI(closing_prices_30min)
            if rsi <= 20:
                rsi = green(rsi)
            if rsi >= 70:
                rsi = red(rsi)
            cpx = closing_prices_5min[-1]
            macd = calcMACD(closing_prices_5min)
            if i == 'USDT-BTC':
                cny_cpx = cpx
                current_btc_usd = cpx
            else:
                cny_cpx = cpx * current_btc_usd * cny_usd

            signal += ''
            if np.diff(np.array(macd)).min() > 0:
                signal += ' macd buy'
                signal = green(signal)
            if np.diff(np.array(macd)).max() < 0:
                signal += ' macd sell'
                signal = red(signal)
            print("{}: \t price: {}\t RSI: {}\tMACD: {}\t {} \t ".format(
                i, round(cny_cpx, 3), str(round(rsi, 3)), ','.join(pretty_macd_list(macd)), signal))
        print("wait 60s\n\n")


    while True:
        get_signal()
        time.sleep(60)
