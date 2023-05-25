import websocket
import json

def on_message(ws, message):print("Message received: {}".format(message))

def on_open(ws):
    print("Established connection")

    request = {"version": "0.0.2"}
    ws.send(json.dumps(request))

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://10.10.11.206:5789/version",
        on_open=on_open,
        on_message=on_message)
    ws.on_open = on_open
    ws.run_forever()