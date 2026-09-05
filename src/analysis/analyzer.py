import pandas as pd


def latest_prices_dataframe(results):
    """
    Convert latest price query results into a Pandas DataFrame.
    """

    columns = [
        "symbol",
        "bucket_start",
        "latest_price"
    ]

    return pd.DataFrame(results, columns=columns)


def volume_dataframe(results):
    """
    Convert volume analytics results into a Pandas DataFrame.
    """

    columns = [
        "symbol",
        "total_volume",
        "avg_volume_per_candle"
    ]

    return pd.DataFrame(results, columns=columns)


def price_change_dataframe(results):
    """
    Convert price change analytics results into a Pandas DataFrame.
    """

    columns = [
        "symbol",
        "first_price",
        "latest_price",
        "price_change",
        "price_change_percent"
    ]

    return pd.DataFrame(results, columns=columns)


def trading_activity_dataframe(results):
    """
    Convert trading activity results into a Pandas DataFrame.
    """

    columns = [
        "symbol",
        "total_trades",
        "avg_trades_per_candle"
    ]

    return pd.DataFrame(results, columns=columns)


def volatility_dataframe(results):
    """
    Convert volatility analytics results into a Pandas DataFrame.
    """

    columns = [
        "symbol",
        "price_range",
        "price_range_percent"
    ]

    return pd.DataFrame(results, columns=columns)


def price_history_dataframe(results):
    """
    Convert price history results into a Pandas DataFrame.
    """

    columns = [
        "bucket_start",
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    return pd.DataFrame(results, columns=columns)