from datetime import datetime, timezone

from src.utils.logger import get_logger


logger = get_logger("processor", "pipeline.log")


def transform_trade(data):
    """
    Transform raw Binance trade data into a clean Python dictionary.
    """
    return {
        "symbol": data["s"],
        "price": float(data["p"]),
        "quantity": float(data["q"]),
        "trade_time": datetime.fromtimestamp(
            data["T"] / 1000,
            tz=timezone.utc
        ),
        "event_time": datetime.fromtimestamp(
            data["E"] / 1000,
            tz=timezone.utc
        )
    }


def validate_trade(trade):
    """
    Validate a transformed trade.
    """

    if not trade["symbol"]:
        logger.warning("Trade rejected: missing symbol")
        return False

    if trade["price"] <= 0:
        logger.warning(
            "Trade rejected: invalid price for %s",
            trade["symbol"]
        )
        return False

    if trade["quantity"] <= 0:
        logger.warning(
            "Trade rejected: invalid quantity for %s",
            trade["symbol"]
        )
        return False

    if trade["trade_time"] is None:
        logger.warning(
            "Trade rejected: missing trade time for %s",
            trade["symbol"]
        )
        return False

    return True


def get_minute_bucket(timestamp):
    """
    Convert a trade timestamp into its 1-minute bucket.
    """
    return timestamp.replace(
        second=0,
        microsecond=0
    )


class TradeAggregator:

    def __init__(self):
        self.buckets = {}

    def add_trade(self, trade):
        """
        Add a trade to its corresponding 1-minute OHLCV bucket.

        Returns a completed bucket if the trade belongs
        to a newer minute.
        """

        symbol = trade["symbol"]
        minute = get_minute_bucket(trade["trade_time"])

        key = (symbol, minute)

        completed_bucket = None

        # Find the latest existing bucket for this symbol
        symbol_buckets = [
            bucket_key
            for bucket_key in self.buckets
            if bucket_key[0] == symbol
        ]

        if symbol_buckets:

            previous_minute = max(
                bucket_key[1]
                for bucket_key in symbol_buckets
            )

            # A new minute has started
            if minute > previous_minute:

                completed_bucket = self.finalize_bucket(
                    symbol,
                    previous_minute
                )

        # Create a new bucket
        if key not in self.buckets:

            self.buckets[key] = {
                "symbol": symbol,
                "minute": minute,
                "open": trade["price"],
                "high": trade["price"],
                "low": trade["price"],
                "close": trade["price"],
                "volume": trade["quantity"],
                "trade_count": 1
            }

        # Update existing bucket
        else:

            bucket = self.buckets[key]

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

        return completed_bucket

    def finalize_bucket(self, symbol, minute):
        """
        Remove and return a completed bucket.
        """

        key = (symbol, minute)

        if key not in self.buckets:
            return None

        return self.buckets.pop(key)