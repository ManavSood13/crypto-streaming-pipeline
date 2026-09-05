def get_10_second_bucket(timestamp):
    """
    Convert a trade timestamp into its 10-second bucket.
    """

    second = (timestamp.second // 10) * 10

    return timestamp.replace(
        second=second,
        microsecond=0
    )


class TradeAggregator:

    def __init__(self):
        self.buckets = {}

    def add_trade(self, trade):
        """
        Add a trade to its corresponding 10-second OHLCV bucket.

        Returns a completed bucket if the trade belongs
        to a newer 10-second bucket.
        """

        symbol = trade["symbol"]

        bucket_time = get_10_second_bucket(
            trade["trade_time"]
        )

        key = (symbol, bucket_time)

        completed_bucket = None

        # Find the latest existing bucket for this symbol
        symbol_buckets = [
            bucket_key
            for bucket_key in self.buckets
            if bucket_key[0] == symbol
        ]

        if symbol_buckets:

            previous_bucket = max(
                bucket_key[1]
                for bucket_key in symbol_buckets
            )

            # A new 10-second bucket has started
            if bucket_time > previous_bucket:

                completed_bucket = self.finalize_bucket(
                    symbol,
                    previous_bucket
                )

        # Create a new bucket
        if key not in self.buckets:

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

    def finalize_bucket(self, symbol, bucket_time):
        """
        Remove and return a completed bucket.
        """

        key = (symbol, bucket_time)

        if key not in self.buckets:
            return None

        return self.buckets.pop(key)