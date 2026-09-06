from datetime import datetime, timezone


def _to_float(value):
    """
    Convert a Binance numeric string, returning None if unusable.
    """

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_datetime(value):
    """
    Convert a Binance millisecond timestamp, returning None if unusable.
    """

    if value is None:
        return None

    try:
        return datetime.fromtimestamp(
            value / 1000,
            tz=timezone.utc
        )
    except (TypeError, ValueError, OSError, OverflowError):
        return None


def transform_trade(data):
    """
    Transform raw Binance trade data into a structured Python dictionary.

    Missing or malformed fields become None rather than raising, so the
    validator is what decides whether a trade is usable. Previously a
    malformed payload raised KeyError here and the validator's required
    field checks could never run.
    """

    return {
        "symbol": data.get("s"),
        "price": _to_float(data.get("p")),
        "quantity": _to_float(data.get("q")),
        "trade_time": _to_datetime(data.get("T")),
        "event_time": _to_datetime(data.get("E"))
    }
