from exchange.data_proxy import DataProxy
from lib.util import red, green


def handle_bar(exchange, p):
    data_proxy = DataProxy(exchange)
    ohlc = data_proxy.ohlc(p, 20, 'oneMin')
    open = [i['open'] for i in ohlc]
    close = [i['close'] for i in ohlc]
    high = [i['high'] for i in ohlc]
    low = [i['low'] for i in ohlc]

    if close[-1] / close[-2] < 0.97:
        print(red('{} down 3%'.format(p)))

    HH = max(high[:2])
    LC = min(close[:2])
    HC = max(close[:2])
    LL = min(low[:2])
    Openprice = open[2]

    current_price = close[2]

    Range = max((HH - LC), (HC - LL))
    K1 = 0.9
    BuyLine = Openprice + K1 * Range

    if current_price > BuyLine:
        print(green("buy signal {}".format(p)))

    case1 = (1 - close[2] / close[0]) >= 0.06
    case2 = close[1] / close[0] <= 0.92
    if case1 or case2:
        print(red('{} sell signal'.format(p)))
