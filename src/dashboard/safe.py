"""
Small helpers for reading values out of dashboard dataframes.

The dashboard runs against whatever the pipeline has written so far,
which may be nothing at all, so every lookup has to tolerate a missing
symbol or an empty frame instead of raising IndexError.
"""

from decimal import Decimal

import pandas as pd


NUMERIC_COLUMNS = (
    "open",
    "high",
    "low",
    "close",
    "volume",
    "latest_price",
    "first_price",
    "price_change",
    "price_change_percent",
    "total_volume",
    "avg_volume_per_candle",
    "total_trades",
    "avg_trades_per_candle",
    "price_range",
    "price_range_percent",
)


def to_float(frame):
    """
    Convert NUMERIC columns from Decimal to float.

    psycopg returns NUMERIC as Decimal, which leaves pandas holding
    object columns: no vectorised maths, and None mixed with Decimal
    instead of NaN, which breaks gap handling in Plotly.
    """

    if frame is None or frame.empty:
        return frame

    for column in frame.columns:
        if column in NUMERIC_COLUMNS:
            frame[column] = pd.to_numeric(
                frame[column],
                errors="coerce"
            )

    return frame


def lookup(frame, symbol, column, default=None):
    """
    Return `column` for `symbol`, or `default` if it is not present.
    """

    if frame is None or frame.empty or "symbol" not in frame.columns:
        return default

    matches = frame.loc[frame["symbol"] == symbol, column]

    if matches.empty:
        return default

    value = matches.iloc[0]

    if value is None or pd.isna(value):
        return default

    if isinstance(value, Decimal):
        return float(value)

    return value


def first_row(frame, column, default=None):
    """
    Return `column` of the first row, or `default` if the frame is empty.
    """

    if frame is None or frame.empty or column not in frame.columns:
        return default

    value = frame.iloc[0][column]

    if value is None or pd.isna(value):
        return default

    if isinstance(value, Decimal):
        return float(value)

    return value


def money(value):
    """
    Format a price, tolerating a missing value.
    """

    if value is None:
        return "—"

    return f"${value:,.2f}"


def percent(value):
    """
    Format a signed percentage, tolerating a missing value.
    """

    if value is None:
        return None

    return f"{value:+.2f}%"
