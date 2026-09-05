import websocket
import json
import time
import signal

from src.utils.logger import get_logger
from src.processing.data_processor import (
    transform_trade,
    validate_trade,
    TradeAggregator
)
from src.database.postgres import (
    get_connection,
    insert_ohlcv
)

logger = get_logger("websocket", "websocket.log")
aggregator = TradeAggregator()
db_connection = get_connection()

# -----------------------------
# Shutdown handling
# -----------------------------

shutdown_requested = False
current_ws = None


def handle_shutdown(signum, frame):
    global shutdown_requested

    shutdown_requested = True
    logger.info("🛑Shutdown requested by user")
    print("\n🛑Shutdown requested. Stopping WebSocket ...")
    
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

    logger.info("WebSocket connected 🤯")
    print("WebSocket connected 🤯")

    # Reset reconnect delay after successful connection
    reconnect_delay = 1


def on_message(ws, message):
    try:
        combined_data = json.loads(message)
        data = combined_data["data"]

        # Transform raw Binance data
        trade = transform_trade(data)

        # Validate transformed data
        if not validate_trade(trade):
            logger.warning("Invalid trade received: %s", trade)
            return

        # Add trade to the appropriate minute bucket
        completed_bucket = aggregator.add_trade(trade)

        # A minute has been completed
        if completed_bucket:
            logger.info(
                "Completed OHLCV: %s",
                completed_bucket
            )

            insert_ohlcv(db_connection, completed_bucket)

            print("SAVED TO DATABASE:", completed_bucket)

    except Exception:
        logger.exception("Error processing WebSocket message")



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


try:
    while not shutdown_requested:
        try:
            logger.info("Connecting to Binance WebSocket...")
            print("Connecting to Binance WebSocket 🥸 ...")

            current_ws = websocket.WebSocketApp(
                url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )

            current_ws.run_forever(
                ping_interval=20,
                ping_timeout=10
            )

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

        print(
            f"Connection lost. Reconnecting in {reconnect_delay} seconds..."
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

finally:
    db_connection.close()
    logger.info("PostgreSQL connection closed")
    logger.info("WebSocket application stopped")

    print("PostgreSQL connection closed")
    print("WebSocket application stopped")