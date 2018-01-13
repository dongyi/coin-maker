"""
在一个平台里寻找套利路径

比如:
1 BTC → ETH → LTC → 1.002 BTC
就可以做

"""

"""

针对一个平台 (taker手续费不要太高)

1. 找到平台上btc-eth的买一和卖一
2. 找到该平台上成交量最大的alt_list, 分别计算btc和eth相对价格的买一和卖一价
3. 如果btc_alt_buy < eth_alt_sell * eth_btc_sell 或者 eth_alt_buy < btc_alt_sell * eth_btc_sell, 就下单



"""