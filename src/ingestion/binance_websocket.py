import websocket
import json
import time
import signal

from src.utils.logger import get_logger


logger = get_logger("websocket", "websocket.log")


# -----------------------------
# Shutdown handling
# -----------------------------

shutdown_requested = False
current_ws = None


def handle_shutdown(signum, frame):
    global shutdown_requested

    logger.info("Shutdown requested by user")

    shutdown_requested = True

    if current_ws is not None:
        current_ws.close()


signal.signal(signal.SIGINT, handle_shutdown)


# -----------------------------
# Reconnection settings
# -----------------------------

reconnect_delay = 1
max_reconnect_delay = 30


# -----------------------------
# WebSocket callbacks
# -----------------------------

def on_open(ws):
    global reconnect_delay

    logger.info("WebSocket connected")

    # Reset reconnect delay after successful connection
    reconnect_delay = 1


def on_message(ws, message):
    combined_data = json.loads(message)
    data = combined_data["data"]

    symbol = data["s"]
    price = data["p"]
    quantity = data["q"]

    trade_time = data["T"]
    event_time = data["E"]

    print(
        f"{symbol} | Price: {price} | "
        f"Quantity: {quantity} | "
        f"Trade Time: {trade_time} | "
        f"Event Time: {event_time}"
    )


def on_error(ws, error):
    logger.error("WebSocket error: %s", error)


def on_close(ws, close_status_code, close_msg):
    logger.warning(
        "WebSocket closed: code=%s message=%s",
        close_status_code,
        close_msg
    )


# -----------------------------
# Binance streams
# -----------------------------

symbols = [
    "btcusdt",
    "ethusdt",
    "bnbusdt",
    "solusdt",
    "xrpusdt",
    "adausdt",
    "dogeusdt",
    "avaxusdt",
    "linkusdt",
    "dotusdt"
]


streams = "/".join(
    f"{symbol}@trade"
    for symbol in symbols
)


url = f"wss://stream.binance.com:9443/stream?streams={streams}"


# -----------------------------
# WebSocket connection loop
# -----------------------------

while not shutdown_requested:

    try:

        logger.info("Connecting to Binance WebSocket")

        current_ws = websocket.WebSocketApp(
            url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        current_ws.run_forever()

    except Exception:
        logger.exception("Unexpected WebSocket failure")

    finally:
        current_ws = None


    # Don't reconnect if user pressed Ctrl+C
    if shutdown_requested:
        break


    logger.warning(
        "Connection lost. Reconnecting in %s seconds...",
        reconnect_delay
    )


    try:
        time.sleep(reconnect_delay)

    except KeyboardInterrupt:
        handle_shutdown(None, None)
        break


    reconnect_delay = min(
        reconnect_delay * 2,
        max_reconnect_delay
    )


logger.info("WebSocket application stopped")