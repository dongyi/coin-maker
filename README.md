# crypto quant

## usage

- fill your exchange api keys in secrets.json

```
{
  "bittrex": {
    "bittrex_key": "xxx",
    "bittrex_secret": "xxx",
    "twilio_key": "TWILIO_API_KEY",
    "twilio_secret": "TWILIO_SECRET",
    "twilio_number": "TWILIO_PHONE_NUMBER",
    "my_number": "xxx"
  },
  "okex" : {
    "apikey": "xxx",
    "secretkey": "xxx"
  }
}

```

- `python app.py`

## exchange APIs

- bittrex

  mostly trade on it

- bter

  public history data

- yunbi

  it was shutdown



## technical analyse

- use api from talib


## following

- more exchange support

- analyse on order_book, trade history

- notify on signal

- automatically trade

- BTC history ohlc analyse