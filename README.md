# crypto quant

## usage

- fill your exchange api keys in secrets.json

```

{
  "bittrex": {
    "api_key": "xx",
    "secret_key": "xx",
    "twilio_key": "TWILIO_API_KEY",
    "twilio_secret": "TWILIO_SECRET",
    "twilio_number": "TWILIO_PHONE_NUMBER",
    "my_number": "+86-11111111111"
  },
  "okex" : {
    "api_key": "xxx",
    "secret_key": "xxx"
  },
  "bigone": {
    "api_key": "xxx",
    "secret_key": "xxx"
  }
}

```

- collect order history  收集成交历史, 写入csv文件

 `python cli.py collect_order --market [BTC-ETH] --exchange [bittrex]`

- watch indicators       监控技术指标, 现在有rsi/macd

 `python cli.py watch_indicator --exchange [bittrex]`

- watch breakout         监控价格突破均线

 `python cli.py find_breakout --exchange bittrex`

- order book analyse     分析盘口

 `python cli.py watch_laplace_indicator --exchange bittrex --pair BTC-1ST`

## exchange APIs

- bittrex

- bter

- yunbi

- okex

- poloniex

- hitbtc

- bitstamp

- bigone

- binance


## technical analyse

- use api from talib


## following

- more exchange support

- analyse on order_book, trade history

- notify on signal

- automatically trade

- BTC history ohlc analyse

## donation

- 比特币乞讨  (bitcoin address):
 
 `3MbdGbkcN834o4WnoCa6QEDrDg72GSmZ72`
 
 
