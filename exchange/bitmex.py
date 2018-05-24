from bitmex_websocket import BitMEXWebsocket
import websocket

TEST_WS_ENTRY = 'https://testnet.bitmex.com/api/v1'
WS_ENTRY = 'wss://www.bitmex.com/realtime'


def on_message(ws):
    print(ws)


def on_error(ws, data):
    print("error")


def on_close(ws):
    print("websocket close")


def on_open(ws):
    print("open websocket")


def show_quotes(pair):
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp('wss://www.bitmex.com/realtime?heartbeat=1&_primuscb=MDoSuCd',
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
