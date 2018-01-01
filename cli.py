import click

from lib.util import *

from ta.indicators import *

from exchange.bittrex import Bittrex

import script.collect_orders

import datetime


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
def find_breakout(exchange):
    from script.find_breakout import runner
    runner(exchange)


@click.command()
@click.option('--exchange', prompt='exchange name')
def watch_indicator(exchange):
    assert exchange == 'bittrex'
    print("===============================================================================")
    print("\t\t\t bittrex indicator")
    print("===============================================================================")

    coin_pairs = ['USDT-BTC', 'BTC-1ST', 'BTC-ETH', 'BTC-OMG', 'BTC-GNT', 'BTC-BCC', 'BTC-SC']

    my_bittrex = Bittrex(*load_api_key('bittrex'))

    def get_signal():
        current_btc_usd = 0.0
        cny_usd = 6.56

        for i in coin_pairs:
            closing_prices_1min = my_bittrex.getClosingPrices(i, 100, 'oneMin')

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

            print("{}: \t price: {}\t\t RSI: {}\tMACD: {}\t {} \t {}".format(
                i, round(cny_cpx, 3), rsi, macd_str, '', ''))
        print("wait 60s\n\n")

    while True:
        get_signal()
        time.sleep(60)


@click.command()
@click.option('--exchange', prompt='exchange name')
def analyse_volatilty(exchange):
    from script.analyse_volatility import get_volatility_df
    get_volatility_df(exchange)


@click.command()
@click.option('--address', prompt='which address you want check')
def plot_ether_transactions(address):
    from etherscan.accounts import Account
    with open('etherscan_api_key.json', mode='r') as key_file:
        key = json.loads(key_file.read())['key']

    api = Account(address=address, api_key=key)
    transactions = api.normal_transactions()

    print(transactions)


@click.command()
@click.option('--pair', prompt='trade pair')
@click.option('--exchange', prompt='exchange name')
def watch_laplace_indicator(pair, exchange):
    from strategy.Laplace import laplace_indicator
    while True:
        value = laplace_indicator(pair, exchange)
        print("{} {} {}".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                pair, value))
        time.sleep(30)


@click.command()
@click.option('--pair', prompt='trade pair')
@click.option('--exchange', prompt='exchange name')
def market_maker(pair, exchange):
    from strategy.market_maker import on_tick
    while True:
        on_tick(pair, exchange)
        time.sleep(30)


cli.add_command(collect_order)
cli.add_command(analyse_volatilty)
cli.add_command(watch_indicator)
cli.add_command(find_breakout)
cli.add_command(plot_ether_transactions)
cli.add_command(watch_laplace_indicator)
cli.add_command(market_maker)

if __name__ == "__main__":
    cli()
