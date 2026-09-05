from datetime import datetime, timezone


def transform_trade(data):
    """
    Transform raw Binance trade data into a structured Python dictionary.
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