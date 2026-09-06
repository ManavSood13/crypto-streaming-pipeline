from datetime import timedelta

from src.utils.logger import get_logger


logger = get_logger("aggregator", "pipeline.log")


BUCKET_SECONDS = 10

# How long to wait past the end of a bucket before assuming
# no further trades will arrive for it.
STALE_GRACE_SECONDS = 5


def get_10_second_bucket(timestamp):
    """
    Convert a trade timestamp into its 10-second bucket.
    """

    second = (timestamp.second // BUCKET_SECONDS) * BUCKET_SECONDS

    return timestamp.replace(
        second=second,
        microsecond=0
    )


class TradeAggregator:
    """
    Aggregate raw trades into fixed-width OHLCV buckets.

    A bucket is completed, and returned for persistence, when any of
    the following happens:

    - a trade arrives for a newer bucket of the same symbol
    - `flush_stale` decides the bucket can no longer receive trades
    - `flush_all` is called during shutdown

    Every method that can complete a bucket returns a *list*, because a
    single event may close more than one bucket.
    """

    def __init__(self, bucket_seconds=BUCKET_SECONDS):
        self.bucket_seconds = bucket_seconds

        # (symbol, bucket_start) -> bucket
        self.buckets = {}

        # symbol -> newest bucket_start seen so far
        self.watermarks = {}

        self.late_trades = 0

    # -----------------------------
    # Ingestion
    # -----------------------------

    def add_trade(self, trade):
        """
        Add a trade to its corresponding OHLCV bucket.

        Returns a list of completed buckets (possibly empty).
        """

        symbol = trade["symbol"]

        bucket_time = get_10_second_bucket(
            trade["trade_time"]
        )

        key = (symbol, bucket_time)
        watermark = self.watermarks.get(symbol)

        # The bucket this trade belongs to has already been persisted,
        # so it can no longer be updated. Count it rather than silently
        # creating a bucket that would never be flushed.
        if (
            key not in self.buckets
            and watermark is not None
            and bucket_time < watermark
        ):
            self.late_trades += 1

            logger.warning(
                "Late trade discarded: %s %s (watermark %s)",
                symbol,
                bucket_time,
                watermark
            )

            return []

        completed = []

        # A newer bucket has started, so every older bucket for this
        # symbol is now closed. Finalising *all* of them (not just the
        # most recent) prevents out-of-order trades leaking buckets.
        if watermark is None or bucket_time > watermark:
            self.watermarks[symbol] = bucket_time
            completed = self._finalize_before(symbol, bucket_time)

        self._apply_trade(key, symbol, bucket_time, trade)

        return completed

    # -----------------------------
    # Flushing
    # -----------------------------

    def flush_stale(self, now, grace_seconds=STALE_GRACE_SECONDS):
        """
        Complete buckets that can no longer receive trades.

        A bucket is stale once its own time window has ended and the
        grace period has passed. This is what rescues symbols that stop
        trading: without it their final bucket is never written.
        """

        cutoff = now - timedelta(
            seconds=self.bucket_seconds + grace_seconds
        )

        stale_keys = [
            key
            for key in self.buckets
            if key[1] <= cutoff
        ]

        return self._pop_keys(stale_keys)

    def flush_all(self):
        """
        Complete and return every open bucket.

        Called on shutdown so in-flight buckets are persisted instead
        of being discarded.
        """

        return self._pop_keys(
            list(self.buckets)
        )

    # -----------------------------
    # Internals
    # -----------------------------

    def _apply_trade(self, key, symbol, bucket_time, trade):

        bucket = self.buckets.get(key)

        if bucket is None:

            self.buckets[key] = {
                "symbol": symbol,
                "bucket_start": bucket_time,
                "open": trade["price"],
                "high": trade["price"],
                "low": trade["price"],
                "close": trade["price"],
                "volume": trade["quantity"],
                "trade_count": 1
            }

            return

        bucket["high"] = max(
            bucket["high"],
            trade["price"]
        )

        bucket["low"] = min(
            bucket["low"],
            trade["price"]
        )

        bucket["close"] = trade["price"]

        bucket["volume"] = round(
            bucket["volume"] + trade["quantity"],
            8
        )

        bucket["trade_count"] += 1

    def _finalize_before(self, symbol, bucket_time):
        """
        Complete every open bucket for `symbol` older than `bucket_time`.
        """

        keys = [
            key
            for key in self.buckets
            if key[0] == symbol and key[1] < bucket_time
        ]

        return self._pop_keys(keys)

    def _pop_keys(self, keys):
        """
        Remove the given buckets and return them oldest-first.
        """

        return [
            self.buckets.pop(key)
            for key in sorted(keys, key=lambda item: (item[1], item[0]))
        ]
