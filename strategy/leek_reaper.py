"""
参数                       默认值  描述
-----------------  ---------  -------------------
BurstThresholdPct      5e-05  burst.threshold.pct
BurstThresholdVol     10      burst.threshold.vol
MinStock               0.1    最小交易量
CalcNetInterval       60      净值计算周期(秒)
BalanceTimeout     10000      平衡等代时间(毫秒)
TickInterval         280      轮训周期(毫秒)

"""

from exchange.data_proxy import DataProxy


"""
TO BE DONE
"""


class LeeksReaper:

    def __init__(self, exchange):
        self.numTick = 0
        self.lastTradeId = 0
        self.vol = 0
        self.askPrice = 0
        self.bidPrice = 0
        self.orderBook = {'Asks': [], 'Bids': []}
        self.prices = []
        self.tradeOrderId = 0
        self.p = 0.5
        self.account = None
        self.preCalc = 0
        self.preNet = 0
        self.__exchange = DataProxy(exchange)

    def updateTrades(self):
        trades = self.__exchange.get_trades()
        if len(self.prices) == 0:
            while len(trades) == 0:
                trades.append(self.__exchange.get_trades())
            for i in range(15):
                self.prices[i] = trades[len(trades) - 1]['Price']
        self.vol = 0.7 * self.vol