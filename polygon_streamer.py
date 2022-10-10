import websocket, json
from config import *

def on_open(ws):
    print("opened")
    auth_data = {
        "action": "auth",
        "params": "GenwEEyWOBCxaKAX4D3bQTKES222SRww"
    }

    ws.send(json.dumps(auth_data))

    channel_data = {
        "action": "subscribe",
        "params": TICKERS
    }
    print(channel_data)
    ws.send(json.dumps(channel_data))


def on_message(ws, message):
    print("received a message")
    print(message)

def on_close(ws):
    print("closed connection")

def on_error(ws, error):
    print(error)

socket = "wss://socket.polygon.io/stocks"

ws = websocket.WebSocketApp(socket, on_open=on_open,
on_message=on_message, on_close=on_close, on_error=on_error)
ws.run_forever()
