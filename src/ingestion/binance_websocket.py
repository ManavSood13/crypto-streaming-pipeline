#modules import
import json
import queue
import signal
import threading
import time
from datetime import datetime, timezone

import websocket

#file imports
from src.utils.logger import get_logger
from src.processing.transformer import transform_trade
from src.processing.validator import validate_trade
from src.processing.aggregator import TradeAggregator
from src.database.connection import get_connection, ensure_connection
from src.database.repository import insert_ohlcv_many


logger = get_logger("binance_websocket", "pipeline.log")


SYMBOLS = [
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


STREAM_URL = (
    "wss://stream.binance.com:9443/stream?streams="
    + "/".join(f"{symbol}@trade" for symbol in SYMBOLS)
)


RECONNECT_DELAY = 1
MAX_RECONNECT_DELAY = 30

# How often to look for buckets belonging to symbols that stopped
# trading. Without this their final bucket is never written.
STALE_CHECK_INTERVAL = 2

# Completed buckets are handed to a writer thread so that database
# latency cannot stall the socket and trip the ping timeout.
WRITE_QUEUE_SIZE = 10000
WRITER_BATCH_TIMEOUT = 0.5


class Pipeline:
    """
    Owns the aggregator, the database connection and the shutdown flag
    for one ingestion run.
    """

    def __init__(self):
        self.aggregator = TradeAggregator()
        self.connection = get_connection()
        self.shutdown_requested = False
        self.current_ws = None
        self.reconnect_delay = RECONNECT_DELAY
        self.last_stale_check = 0.0
        self.saved = 0
        self.dropped = 0

        self.write_queue = queue.Queue(maxsize=WRITE_QUEUE_SIZE)
        self.writer_stopped = threading.Event()

        self.writer_thread = threading.Thread(
            target=self._writer_loop,
            name="ohlcv-writer",
            daemon=True
        )

    # -----------------------------
    # Persistence
    # -----------------------------

    def enqueue(self, buckets):
        """
        Hand completed buckets to the writer thread.

        Called from the socket thread, so it must never block.
        """

        for bucket in buckets:
            try:
                self.write_queue.put_nowait(bucket)
            except queue.Full:
                self.dropped += 1
                logger.error(
                    "Write queue full, dropped bucket: %s %s",
                    bucket["symbol"],
                    bucket["bucket_start"]
                )

    def _writer_loop(self):
        """
        Drain the queue and write batches until told to stop.
        """

        while True:
            batch = self._drain_queue()

            if batch:
                self.persist(batch)

            elif self.writer_stopped.is_set():
                return

    def _drain_queue(self):
        """
        Collect whatever is currently queued, waiting briefly if empty.
        """

        batch = []

        try:
            batch.append(
                self.write_queue.get(timeout=WRITER_BATCH_TIMEOUT)
            )
        except queue.Empty:
            return batch

        while True:
            try:
                batch.append(self.write_queue.get_nowait())
            except queue.Empty:
                break

        return batch

    def persist(self, buckets):
        """
        Write completed buckets, reconnecting if the connection died.

        Runs on the writer thread only, so the connection has a single
        owner.
        """

        if not buckets:
            return

        try:
            self.connection = ensure_connection(self.connection)
            written = insert_ohlcv_many(self.connection, buckets)

        except Exception:
            # One retry on a fresh connection covers a server restart
            # or a dropped socket mid-write.
            logger.exception("Insert failed, retrying on a new connection")

            try:
                self.connection = ensure_connection(None)
                written = insert_ohlcv_many(self.connection, buckets)

            except Exception:
                logger.exception(
                    "Retry failed, %s bucket(s) could not be saved",
                    len(buckets)
                )
                return

        self.saved += written

        for bucket in buckets:
            logger.info(
                "Saved OHLCV: %s %s O=%s H=%s L=%s C=%s V=%s N=%s",
                bucket["symbol"],
                bucket["bucket_start"],
                bucket["open"],
                bucket["high"],
                bucket["low"],
                bucket["close"],
                bucket["volume"],
                bucket["trade_count"]
            )

    def flush_stale(self):
        """
        Persist buckets whose time window has closed.
        """

        now = time.monotonic()

        if now - self.last_stale_check < STALE_CHECK_INTERVAL:
            return

        self.last_stale_check = now

        self.enqueue(
            self.aggregator.flush_stale(
                datetime.now(timezone.utc)
            )
        )

    def shutdown(self):
        """
        Persist every in-flight bucket and close the connection.
        """

        remaining = self.aggregator.flush_all()

        if remaining:
            logger.info(
                "Flushing %s in-flight bucket(s) before exit",
                len(remaining)
            )
            self.enqueue(remaining)

        # Let the writer finish everything still queued.
        self.writer_stopped.set()

        if self.writer_thread.is_alive():
            self.writer_thread.join(timeout=30)

        if self.connection is not None and not self.connection.closed:
            self.connection.close()

        logger.info(
            "PostgreSQL connection closed (%s bucket(s) saved this run, "
            "%s late trade(s) discarded, %s dropped)",
            self.saved,
            self.aggregator.late_trades,
            self.dropped
        )

    # -----------------------------
    # WebSocket callbacks
    # -----------------------------

    def on_open(self, ws):
        logger.info("WebSocket connected")
        print("WebSocket connected")

        self.reconnect_delay = RECONNECT_DELAY

    def on_message(self, ws, message):
        try:
            payload = json.loads(message)

            # Control frames (subscription acks) carry no "data" key.
            data = payload.get("data")

            if not isinstance(data, dict) or data.get("e") != "trade":
                return

            trade = transform_trade(data)

            if not validate_trade(trade):
                return

            self.enqueue(
                self.aggregator.add_trade(trade)
            )

        except Exception:
            logger.exception("Error processing WebSocket message")

        # Runs on the socket thread, but is rate limited and only
        # touches the database when a bucket has actually expired.
        self.flush_stale()

    def on_error(self, ws, error):
        logger.error("WebSocket error: %s", error)

    def on_close(self, ws, close_status_code, close_msg):
        logger.warning(
            "WebSocket closed: code=%s message=%s",
            close_status_code,
            close_msg
        )

    # -----------------------------
    # Run loop
    # -----------------------------

    def run(self):
        self.writer_thread.start()

        try:
            while not self.shutdown_requested:
                try:
                    print("Connecting to Binance WebSocket ...")

                    self.current_ws = websocket.WebSocketApp(
                        STREAM_URL,
                        on_open=self.on_open,
                        on_message=self.on_message,
                        on_error=self.on_error,
                        on_close=self.on_close
                    )

                    self.current_ws.run_forever(
                        ping_interval=20,
                        ping_timeout=10
                    )

                except Exception:
                    logger.exception("Unexpected WebSocket failure")

                finally:
                    self.current_ws = None

                if self.shutdown_requested:
                    break

                logger.warning(
                    "Connection lost. Reconnecting in %s seconds...",
                    self.reconnect_delay
                )

                print(
                    f"Connection lost. Reconnecting in "
                    f"{self.reconnect_delay} seconds..."
                )

                try:
                    time.sleep(self.reconnect_delay)
                except KeyboardInterrupt:
                    self.request_shutdown()
                    break

                self.reconnect_delay = min(
                    self.reconnect_delay * 2,
                    MAX_RECONNECT_DELAY
                )

        finally:
            self.shutdown()
            print("WebSocket application stopped")

    def request_shutdown(self):
        self.shutdown_requested = True

        logger.info("Shutdown requested by user")
        print("\nShutdown requested. Flushing and stopping ...")

        if self.current_ws is not None:
            self.current_ws.close()


def main():
    pipeline = Pipeline()

    def handle_shutdown(signum, frame):
        pipeline.request_shutdown()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    pipeline.run()


if __name__ == "__main__":
    main()
