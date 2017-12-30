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

from exchange.data_proxy import DataProxy


def on_tick():
    # run in loop outside 3s/tick
    pass

