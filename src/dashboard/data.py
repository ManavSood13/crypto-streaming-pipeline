import streamlit as st

from src.database.connection import get_connection, is_alive

from src.analytics.queries import (
    get_latest_prices,
    get_volume_by_symbol,
    get_price_history,
    get_total_candles,
    get_price_change,
    get_trading_activity,
    get_volatility,
    get_volume_over_time,
    get_pipeline_health,
)

from src.analysis.analyzer import (
    latest_prices_dataframe,
    volume_dataframe,
    price_change_dataframe,
    trading_activity_dataframe,
    volatility_dataframe,
    volume_over_time_dataframe,
    price_history_dataframe,
)

from src.dashboard.safe import to_float


@st.cache_resource(show_spinner=False)
def _connection():
    """
    One PostgreSQL connection shared by every dashboard rerun.

    Opening a connection costs more than running all of the dashboard
    queries put together, and the fragment reruns every few seconds, so
    the connection is cached for the lifetime of the Streamlit process.
    """

    return get_connection()


def get_cached_connection():
    """
    Return the shared connection, reopening it if it has died.
    """

    connection = _connection()

    if not is_alive(connection):
        _connection.clear()
        connection = _connection()

    return connection


def get_dashboard_data():
    """
    Fetch all dashboard data using the shared PostgreSQL connection.
    """

    connection = get_cached_connection()

    return {
        "latest_df": to_float(
            latest_prices_dataframe(
                get_latest_prices(connection)
            )
        ),
        "volume_df": to_float(
            volume_dataframe(
                get_volume_by_symbol(connection)
            )
        ),
        "price_change_df": to_float(
            price_change_dataframe(
                get_price_change(connection)
            )
        ),
        "trading_activity_df": to_float(
            trading_activity_dataframe(
                get_trading_activity(connection)
            )
        ),
        "volatility_df": to_float(
            volatility_dataframe(
                get_volatility(connection)
            )
        ),
        "volume_over_time_df": to_float(
            volume_over_time_dataframe(
                get_volume_over_time(connection)
            )
        ),
        "total_candles": get_total_candles(connection),
        "health": get_pipeline_health(connection),
        "connection": connection,
    }


def get_price_history_data(
    connection,
    symbol,
    limit
):
    """
    Fetch price history using the existing PostgreSQL connection.
    """

    return to_float(
        price_history_dataframe(
            get_price_history(
                connection,
                symbol,
                limit
            )
        )
    )
