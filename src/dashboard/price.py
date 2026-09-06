import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.dashboard.data import get_price_history_data
from src.dashboard.safe import lookup, money, percent


def add_data_gaps(history_df, bucket_seconds=10):
    """
    Insert a gap row wherever consecutive candles are missing.

    Plotly only breaks a line on NaN, so a placeholder row is inserted
    after every candle that is followed by a jump larger than one
    bucket. Building this with a boolean mask keeps the numeric columns
    as floats; the original row-by-row rebuild turned them into objects,
    which stopped the gaps from rendering.
    """

    if history_df.empty:
        return history_df

    history_df = history_df.sort_values(
        "bucket_start"
    ).reset_index(drop=True)

    time_difference = (
        history_df["bucket_start"]
        .diff()
        .shift(-1)
        .dt.total_seconds()
    )

    gap_positions = history_df.index[
        time_difference > bucket_seconds
    ]

    if gap_positions.empty:
        return history_df

    gaps = pd.DataFrame(
        {
            "bucket_start": pd.NaT,
            "open": float("nan"),
            "high": float("nan"),
            "low": float("nan"),
            "close": float("nan"),
            "volume": float("nan"),
        },
        index=gap_positions + 0.5,
    )

    return (
        pd.concat([history_df, gaps])
        .sort_index()
        .reset_index(drop=True)
    )


def render_price_analysis(
    latest_df,
    price_change_df,
    connection
):

    st.subheader("Price Analysis")

    selector_col, timeframe_col = st.columns(
        [3, 1],
        gap="medium"
    )

    symbols = (
        latest_df["symbol"].tolist()
        if latest_df is not None and not latest_df.empty
        else []
    )

    if not symbols:
        st.info("No market data yet. Start the ingestion pipeline.")
        return

    with selector_col:

        selected_symbol = st.selectbox(
            "Cryptocurrency",
            symbols
        )

    with timeframe_col:

        timeframe = st.selectbox(
            "Timeframe",
            [
                "10 minutes",
                "30 minutes",
                "60 minutes"
            ],
            index=0
        )

    timeframe_limits = {
        "10 minutes": 60,
        "30 minutes": 180,
        "60 minutes": 360
    }

    history_limit = timeframe_limits[
        timeframe
    ]

    history_df = get_price_history_data(
        connection,
        selected_symbol,
        history_limit
    )

    selected_price = lookup(
        latest_df,
        selected_symbol,
        "latest_price"
    )

    selected_change = lookup(
        price_change_df,
        selected_symbol,
        "price_change_percent"
    )

    price_col1, price_col2 = st.columns(
        [4, 1],
        gap="medium"
    )

    with price_col1:

        st.markdown(
            f"### {selected_symbol} Price History"
        )

    with price_col2:

        st.metric(
            "Current Price",
            money(selected_price),
            delta=percent(selected_change)
        )

    if history_df.empty:
        st.info(f"No price history stored for {selected_symbol} yet.")
        return

    history_df = add_data_gaps(
        history_df
    )

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=history_df["bucket_start"],
            y=history_df["close"],
            mode="lines",
            name=selected_symbol,
            connectgaps=False
        )
    )

    figure.update_layout(
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        height=420,
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10
        ),
        hovermode="x unified"
    )

    st.plotly_chart(
        figure,
        width="stretch"
    )