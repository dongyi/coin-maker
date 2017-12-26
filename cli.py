import click
import json

from lib.util import *
# from twilio.rest import Client
from ta.indicators import *

from exchange.bittrex import Bittrex
from exchange.bittrex import getClosingPrices

import script.collect_orders


@click.group()
def cli():
    pass



@click.command()
@click.option('--market', prompt='market pair')
@click.option('--exchange', prompt='exchange name')
def collect_order(market, exchange):
    script.collect_orders.runner(exchange, market)




@click.command()
@click.option('--exchange', prompt='exchange name')
def watch_indicator(exchange):
    assert exchange == 'bittrex'
    print("===============================================================================")
    print("\t\t\t bittrex indicator")
    print("===============================================================================")

    coin_pairs = ['USDT-BTC', 'BTC-1ST', 'BTC-ETH', 'BTC-OMG', 'BTC-GNT', 'BTC-BCC', 'BTC-NEO']

    my_bittrex = Bittrex(*load_api_key('bittrex'))

    def get_signal():
        current_btc_usd = 0.0
        cny_usd = 6.56

        for i in coin_pairs:
            closing_prices_1min = getClosingPrices(my_bittrex, i, 100, 'oneMin')

            ohlc = my_bittrex.getHistoricalData(i, period=30, unit='fiveMin')
            breakout = findBreakout(ohlc, 30)
            if breakout != 'hold':
                breakout = red(breakout)
            rsi = calculateRSI(np.array(closing_prices_1min))[-1]
            rsi = round(rsi, 3)
            if rsi <= 20:
                rsi = green(rsi)
            elif rsi >= 70:
                rsi = red(rsi)
            cpx = closing_prices_1min[-1]
            macd = calcMACD(np.array(closing_prices_1min))
            if i == 'USDT-BTC':
                cny_cpx = cpx
                current_btc_usd = cpx
            else:
                cny_cpx = cpx * current_btc_usd * cny_usd

            macd_str = ','.join(pretty_macd_list(macd))

            if np.diff(np.array(macd)).min() > 0:
                macd_str = green(macd_str)
            if np.diff(np.array(macd)).max() < 0:
                macd_str = red(macd_str)

            print("{}: \t price: {}\t\t RSI: {}\tMACD: {}\t {} \t breakout: {}".format(
                i, round(cny_cpx, 3), rsi, macd_str, '', breakout))
        print("wait 60s\n\n")


    while True:
        get_signal()
        time.sleep(60)


cli.add_command(collect_order)
cli.add_command(watch_indicator)


if __name__ == "__main__":
    cli()
