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
    "my_number": "+86-18601643984"
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

- collect order history

 `python cli.py collect_order --market [BTC-1ST] --exchange [bittrex]`

- watch indicators

 `python cli.py watch_indicator --exchange [bittrex]`

## exchange APIs

- bittrex

- bter

- yunbi

- okex

- poloniex

- hitbtc

- bitstamp

- bigone


## technical analyse

- use api from talib


## following

- more exchange support

- analyse on order_book, trade history

- notify on signal

- automatically trade

- BTC history ohlc analyse