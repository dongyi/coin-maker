"""
function GetPrice(Type) {
    var depth=_C(exchange.GetDepth);
    var amountBids=0;
    var amountAsks=0;
    //计算买价，获取累计深度达到预设的价格
    if(Type=="Buy"){
       for(var i=0;i<20;i++){
           amountBids+=depth.Bids[i].Amount;
           if (amountBids>floatamountbuy){
               //稍微加0.01，使得订单排在前面
              return depth.Bids[i].Price+0.01;}
        }
    }
    //同理计算卖价
    if(Type=="Sell"){
       for(var j=0; j<20; j++){
    	   amountAsks+=depth.Asks[j].Amount;
            if (amountAsks>floatamountsell){
            return depth.Asks[j].Price-0.01;}
        }
    }
    //遍历了全部深度仍未满足需求，就返回一个价格，以免出现bug
    return depth.Asks[0].Price
}
/*
每个循环的主函数onTick(),这里定的循环时间3.5s，每次循环都会把原来的单子撤销，重新挂单，越简单越不会遇到bug.
*/
function onTick() {
    var buyPrice = GetPrice("Buy");
    var sellPrice= GetPrice("Sell");
    //买卖价差如果小于预设值，就会挂一个相对更深的价格
    if ((sellPrice - buyPrice) <= diffprice){
            buyPrice-=10;
            sellPrice+=10;}
    //把原有的单子全部撤销，实际上经常出现新的价格和已挂单价格相同的情况，此时不需要撤销
    CancelPendingOrders()
    //获取账户信息，确定目前账户存在多少钱和多少币
    var account=_C(exchange.GetAccount);
    //可买的比特币量
    var amountBuy = _N((account.Balance / buyPrice-0.1),2);
    //可卖的比特币量，注意到没有仓位的限制，有多少就买卖多少，因为我当时的钱很少
    var amountSell = _N((account.Stocks),2);
    if (amountSell > 0.02) {
        exchange.Sell(sellPrice,amountSell);}
    if (amountBuy > 0.02) {
        exchange.Buy(buyPrice, amountBuy);}
    //休眠，进入下一轮循环
    Sleep(sleeptime);
}
"""
from lib.util import fail_default
from lib.util import red, green
from lib.util import human_format

from exchange.bittrex import Bittrex

from exchange.data_proxy import DataProxy

import datetime
import dateutil.parser
import time
import pandas as pd
import gevent
from gevent import monkey

monkey.patch_time()
monkey.patch_socket()
monkey.patch_signal()
monkey.patch_os()

monkey.patch_dns()
monkey.patch_sys()

from exchange.data_proxy import DataProxy

SPREAD_THRESHOLD = 0.1


def on_tick(pair, exchange):
    my_sell_order = 0
    my_buy_order = 0
    # run in loop outside 3s/tick
    data_api = DataProxy(exchange)
    order_slice = data_api.order_books(pair, 100)['result']
    print(order_slice)
    buy_orders = order_slice['buy']
    sell_orders = order_slice['sell']
    spread = buy_orders[0]['Rate'] - sell_orders[0]['Rate']
    print('spread: ', spread)
    if spread < SPREAD_THRESHOLD:
        my_sell_order += 10
        my_buy_order -= 10


def maker(p, exchange):
    while True:
        data_api = DataProxy(exchange)
        ob = data_api.order_books(p, 10)
        assert ob['success']
        best_buy_price = ob['result']['buy'][0]['Rate']
        best_sell_price = ob['result']['sell'][0]['Rate']
        market_width = abs((best_buy_price - best_sell_price) / (best_buy_price + best_sell_price) / 2.0) * 100
        if market_width > 5:
            print("ERROR: market width is too wide, will not place orders")
            time.sleep(30)
            continue
        midmarket = (best_buy_price + best_sell_price) / 2.0
        print(p, market_width, "mid price: ", midmarket)

        """
        es.printOrderBook()
        es.printTrades()

        ordersPerSide = 1
        sellOrdersToPlace = ordersPerSide - len(es.my_orders_sells)
        sellVolumeToPlace = 1
        buyOrdersToPlace = ordersPerSide - len(es.my_orders_buys)
        buyVolumeToPlace = 1
        expires = es.getBlockNumber() + 10

        marginfactor = 0.25

        # Create sell orders
        for sellordernr in range(1, sellOrdersToPlace + 1):
            price = midmarket + sellordernr * midmarket * marginfactor
            amount = sellVolumeToPlace / sellOrdersToPlace
            order = es.createOrder('sell', expires, price, amount, token, userAccount, user_wallet_private_key)
            es.send_message(order)

        # Create buy orders
        for buyordernr in range(1, buyOrdersToPlace + 1):
            price = midmarket - buyordernr * midmarket * marginfactor
            amount = float(buyVolumeToPlace) / float(price) / float(buyOrdersToPlace)
            order = es.createOrder('buy', expires, price, amount, token, userAccount, user_wallet_private_key)
            es.send_message(order)

        print("Printing the user's order book every 30 seconds...")
        while True:
            es.printMyOrderBook()
            time.sleep(30)
        """
        time.sleep(30)


def run_robot(exchange):
    pairs = ['USDT-BTC', 'BTC-1ST', 'BTC-ETH', 'BTC-OMG', 'BTC-GNT', 'BTC-BCC', 'BTC-SC']
    l = []
    for p in pairs:
        l.append(gevent.spawn(maker, p, exchange))

    gevent.joinall(l)
