from datetime import datetime, timezone

import pandas as pd
import pytest

from src.processing.transformer import transform_trade
from src.processing.validator import validate_trade
from src.dashboard.safe import lookup, first_row, money, percent, to_float


RAW_TRADE = {
    "e": "trade",
    "s": "BTCUSDT",
    "p": "80000.50",
    "q": "0.125",
    "T": 1767225600000,
    "E": 1767225600100,
}


# -----------------------------
# Transformation
# -----------------------------

def test_transform_converts_types():
    trade = transform_trade(RAW_TRADE)

    assert trade["symbol"] == "BTCUSDT"
    assert trade["price"] == 80000.50
    assert trade["quantity"] == 0.125
    assert trade["trade_time"].tzinfo is not None
    assert trade["event_time"].tzinfo is not None


def test_transform_uses_utc():
    trade = transform_trade(RAW_TRADE)
    assert trade["trade_time"].utcoffset().total_seconds() == 0


def test_transform_returns_none_for_missing_fields():
    """A malformed payload must reach the validator, not raise."""

    trade = transform_trade({"s": "BTCUSDT"})

    assert trade["symbol"] == "BTCUSDT"
    assert trade["price"] is None
    assert trade["quantity"] is None
    assert trade["trade_time"] is None


def test_transform_returns_none_for_unparseable_numbers():
    trade = transform_trade({**RAW_TRADE, "p": "not-a-number"})
    assert trade["price"] is None


def test_malformed_payload_is_rejected_by_validator():
    """The validator's required-field checks were unreachable before."""

    assert validate_trade(transform_trade({"s": "BTCUSDT"})) is False
    assert validate_trade(transform_trade({})) is False


# -----------------------------
# Validation
# -----------------------------

def valid_trade(**overrides):
    trade = {
        "symbol": "BTCUSDT",
        "price": 80000.0,
        "quantity": 0.5,
        "trade_time": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }
    trade.update(overrides)
    return trade


def test_valid_trade_accepted():
    assert validate_trade(valid_trade()) is True


@pytest.mark.parametrize("field", ["symbol", "price", "quantity", "trade_time"])
def test_missing_field_rejected(field):
    trade = valid_trade()
    del trade[field]
    assert validate_trade(trade) is False


@pytest.mark.parametrize("field", ["symbol", "price", "quantity", "trade_time"])
def test_none_field_rejected(field):
    assert validate_trade(valid_trade(**{field: None})) is False


def test_empty_symbol_rejected():
    assert validate_trade(valid_trade(symbol="")) is False


@pytest.mark.parametrize("price", [0, -1, -0.001])
def test_invalid_price_rejected(price):
    assert validate_trade(valid_trade(price=price)) is False


@pytest.mark.parametrize("quantity", [0, -1, -0.001])
def test_invalid_quantity_rejected(quantity):
    assert validate_trade(valid_trade(quantity=quantity)) is False


# -----------------------------
# Dashboard safety helpers
# -----------------------------

def test_lookup_on_empty_frame_returns_default():
    frame = pd.DataFrame([], columns=["symbol", "latest_price"])
    assert lookup(frame, "BTCUSDT", "latest_price") is None


def test_lookup_missing_symbol_returns_default():
    frame = pd.DataFrame([{"symbol": "ETHUSDT", "latest_price": 2500.0}])
    assert lookup(frame, "BTCUSDT", "latest_price") is None


def test_lookup_finds_value():
    frame = pd.DataFrame([{"symbol": "BTCUSDT", "latest_price": 80000.0}])
    assert lookup(frame, "BTCUSDT", "latest_price") == 80000.0


def test_first_row_on_empty_frame_returns_default():
    frame = pd.DataFrame([], columns=["symbol"])
    assert first_row(frame, "symbol", "—") == "—"


def test_formatters_tolerate_missing_values():
    assert money(None) == "—"
    assert percent(None) is None
    assert money(1234.5) == "$1,234.50"
    assert percent(-2.5) == "-2.50%"


def test_to_float_converts_decimal_columns():
    from decimal import Decimal

    frame = pd.DataFrame([{"symbol": "BTCUSDT", "close": Decimal("80000.5")}])
    assert frame["close"].dtype == object

    converted = to_float(frame)
    assert converted["close"].dtype == "float64"


# -----------------------------
# Volume-over-time chart
# -----------------------------

def test_volume_chart_always_draws_markers():
    """A single bucket must still be visible; a bare line draws nothing."""

    from src.dashboard.charts import create_volume_over_time_chart

    frame = pd.DataFrame(
        [{
            "bucket_time": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "total_volume": 5.0,
        }]
    )

    figure = create_volume_over_time_chart(frame)

    assert "markers" in figure.data[0].mode
    assert len(figure.data[0].x) == 1


def test_volume_chart_handles_empty_frame():
    from src.dashboard.charts import create_volume_over_time_chart

    frame = pd.DataFrame([], columns=["bucket_time", "total_volume"])

    assert create_volume_over_time_chart(frame) is not None
