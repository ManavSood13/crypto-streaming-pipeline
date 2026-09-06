from datetime import datetime, timezone

from src.processing.aggregator import TradeAggregator, get_10_second_bucket


def trade(second, price=100.0, quantity=1.0, symbol="BTCUSDT", minute=0):
    return {
        "symbol": symbol,
        "price": price,
        "quantity": quantity,
        "trade_time": datetime(
            2026, 1, 1, 0, minute, second, tzinfo=timezone.utc
        ),
    }


# -----------------------------
# Bucket assignment
# -----------------------------

def test_bucket_floors_to_ten_seconds():
    assert get_10_second_bucket(trade(7)["trade_time"]).second == 0
    assert get_10_second_bucket(trade(10)["trade_time"]).second == 10
    assert get_10_second_bucket(trade(19)["trade_time"]).second == 10
    assert get_10_second_bucket(trade(59)["trade_time"]).second == 50


def test_bucket_clears_microseconds():
    stamp = datetime(2026, 1, 1, 0, 0, 13, 456789, tzinfo=timezone.utc)
    assert get_10_second_bucket(stamp).microsecond == 0


# -----------------------------
# OHLCV correctness
# -----------------------------

def test_ohlcv_values():
    aggregator = TradeAggregator()

    for price, quantity in [(100, 1), (105, 2), (95, 3), (102, 4)]:
        aggregator.add_trade(trade(1, price=price, quantity=quantity))

    bucket = aggregator.flush_all()[0]

    assert bucket["open"] == 100
    assert bucket["high"] == 105
    assert bucket["low"] == 95
    assert bucket["close"] == 102
    assert bucket["volume"] == 10
    assert bucket["trade_count"] == 4


def test_symbols_are_independent():
    aggregator = TradeAggregator()

    aggregator.add_trade(trade(1, price=100, symbol="BTCUSDT"))
    aggregator.add_trade(trade(1, price=50, symbol="ETHUSDT"))

    buckets = {b["symbol"]: b for b in aggregator.flush_all()}

    assert buckets["BTCUSDT"]["close"] == 100
    assert buckets["ETHUSDT"]["close"] == 50


# -----------------------------
# Completion on a newer bucket
# -----------------------------

def test_new_bucket_completes_previous():
    aggregator = TradeAggregator()

    assert aggregator.add_trade(trade(1)) == []

    completed = aggregator.add_trade(trade(11))

    assert len(completed) == 1
    assert completed[0]["bucket_start"].second == 0


def test_skipping_ahead_completes_every_open_bucket():
    """The original code only ever closed the most recent bucket."""

    aggregator = TradeAggregator()

    aggregator.add_trade(trade(1))
    aggregator.add_trade(trade(11))
    completed = aggregator.add_trade(trade(25))

    assert [b["bucket_start"].second for b in completed] == [10]

    aggregator = TradeAggregator()
    aggregator.add_trade(trade(1, symbol="X"))
    aggregator.buckets[("X", get_10_second_bucket(trade(11)["trade_time"]))] = {
        "symbol": "X",
        "bucket_start": get_10_second_bucket(trade(11)["trade_time"]),
        "open": 1, "high": 1, "low": 1, "close": 1,
        "volume": 1, "trade_count": 1,
    }

    completed = aggregator.add_trade(trade(25, symbol="X"))

    assert len(completed) == 2


# -----------------------------
# Regression: data loss on shutdown
# -----------------------------

def test_flush_all_returns_in_flight_buckets():
    aggregator = TradeAggregator()

    aggregator.add_trade(trade(1))
    aggregator.add_trade(trade(5))

    remaining = aggregator.flush_all()

    assert len(remaining) == 1
    assert remaining[0]["trade_count"] == 2
    assert aggregator.buckets == {}


# -----------------------------
# Regression: quiet symbols
# -----------------------------

def test_flush_stale_completes_expired_buckets():
    aggregator = TradeAggregator()

    aggregator.add_trade(trade(1))

    now = datetime(2026, 1, 1, 0, 0, 30, tzinfo=timezone.utc)
    stale = aggregator.flush_stale(now)

    assert len(stale) == 1
    assert stale[0]["bucket_start"].second == 0


def test_flush_stale_keeps_current_bucket():
    aggregator = TradeAggregator()

    aggregator.add_trade(trade(1))

    now = datetime(2026, 1, 1, 0, 0, 3, tzinfo=timezone.utc)

    assert aggregator.flush_stale(now) == []
    assert len(aggregator.buckets) == 1


# -----------------------------
# Regression: out-of-order leak
# -----------------------------

def test_late_trade_is_discarded_not_leaked():
    aggregator = TradeAggregator()

    aggregator.add_trade(trade(1))
    aggregator.add_trade(trade(11))

    assert aggregator.add_trade(trade(3)) == []
    assert aggregator.late_trades == 1
    assert len(aggregator.buckets) == 1


def test_out_of_order_within_open_bucket_still_counts():
    aggregator = TradeAggregator()

    aggregator.add_trade(trade(5))
    aggregator.add_trade(trade(1))

    bucket = aggregator.flush_all()[0]

    assert bucket["trade_count"] == 2
