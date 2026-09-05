import streamlit as st
import plotly.express as px
import pandas as pd

from src.database.connection import get_connection

from src.analytics.queries import (
    get_latest_prices,
    get_volume_by_symbol,
    get_price_history,
    get_total_candles,
    get_price_change,
    get_trading_activity,
    get_volatility,
    get_hourly_volume
)

from src.analysis.analyzer import (
    latest_prices_dataframe,
    price_history_dataframe
)


st.set_page_config(
    page_title="Crypto Streaming Pipeline",
    page_icon="₿",
    layout="wide"
)


st.title("₿ Crypto Streaming Pipeline")
st.subheader("Real-Time Cryptocurrency Market Dashboard")


@st.fragment(run_every="3s")
def live_dashboard():

    connection = get_connection()

    try:

        # ------------------------------------------------
        # EVERYTHING FROM YOUR CURRENT try BLOCK
        # ------------------------------------------------

        latest_results = get_latest_prices(connection)

        latest_df = latest_prices_dataframe(
            latest_results
        )


        volume_results = get_volume_by_symbol(
            connection
        )

        volume_df = pd.DataFrame(
            volume_results,
            columns=[
                "symbol",
                "total_volume",
                "avg_volume_per_candle"
            ]
        )


        price_change_results = get_price_change(
            connection
        )

        price_change_df = pd.DataFrame(
            price_change_results,
            columns=[
                "symbol",
                "first_price",
                "latest_price",
                "price_change",
                "price_change_percent"
            ]
        )


        total_candles = get_total_candles(
            connection
        )


        # ------------------------------------------------
        # METRIC CARDS
        # ------------------------------------------------

        btc_price = latest_df.loc[
            latest_df["symbol"] == "BTCUSDT",
            "latest_price"
        ].iloc[0]

        eth_price = latest_df.loc[
            latest_df["symbol"] == "ETHUSDT",
            "latest_price"
        ].iloc[0]

        top_volume_symbol = volume_results[0][0]


        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "BTC Price",
                f"${btc_price:,.2f}"
            )

        with col2:
            st.metric(
                "ETH Price",
                f"${eth_price:,.2f}"
            )

        with col3:
            st.metric(
                "Top Volume",
                top_volume_symbol
            )

        with col4:
            st.metric(
                "Total Candles",
                f"{total_candles:,}"
            )


        # ------------------------------------------------
        # LATEST MARKET DATA
        # ------------------------------------------------

        st.subheader("Latest Market Data")

        st.dataframe(
            latest_df,
            width="stretch"
        )


        # ------------------------------------------------
        # CRYPTOCURRENCY SELECTOR
        # ------------------------------------------------

        symbols = latest_df["symbol"].tolist()

        selected_symbol = st.selectbox(
            "Select cryptocurrency",
            symbols
        )


        # ------------------------------------------------
        # PRICE HISTORY
        # ------------------------------------------------

        history_results = get_price_history(
            connection,
            selected_symbol,
            60
        )

        history_df = price_history_dataframe(
            history_results
        )


        st.subheader(
            f"{selected_symbol} Price History"
        )

        st.line_chart(
            history_df,
            x="bucket_start",
            y="close"
        )


        # ------------------------------------------------
        # TRADING VOLUME
        # ------------------------------------------------

        st.subheader(
            "Trading Volume by Cryptocurrency"
        )

        volume_chart_df = volume_df.sort_values(
            "total_volume",
            ascending=True
        )


        fig = px.bar(
            volume_chart_df,
            x="total_volume",
            y="symbol",
            orientation="h",
            title="Total Trading Volume"
        )


        fig.update_layout(
            xaxis_title="Total Volume",
            yaxis_title="Cryptocurrency"
        )


        st.plotly_chart(
            fig,
            width="stretch"
        )


        # ------------------------------------------------
        # PRICE PERFORMANCE
        # ------------------------------------------------

        st.subheader(
            "Price Performance by Cryptocurrency"
        )


        price_change_chart_df = price_change_df.sort_values(
            "price_change_percent",
            ascending=True
        )


        fig = px.bar(
            price_change_chart_df,
            x="price_change_percent",
            y="symbol",
            orientation="h",
            title="Price Change (%)"
        )


        fig.update_layout(
            xaxis_title="Price Change (%)",
            yaxis_title="Cryptocurrency"
        )


        st.plotly_chart(
            fig,
            width="stretch"
        )


        # ------------------------------------------------
        # TRADING ACTIVITY
        # ------------------------------------------------

        trading_activity_results = get_trading_activity(
            connection
        )


        trading_activity_df = pd.DataFrame(
            trading_activity_results,
            columns=[
                "symbol",
                "total_trades",
                "avg_trades_per_candle"
            ]
        )


        st.subheader(
            "Trading Activity by Cryptocurrency"
        )


        trading_activity_chart_df = trading_activity_df.sort_values(
            "total_trades",
            ascending=True
        )


        fig = px.bar(
            trading_activity_chart_df,
            x="total_trades",
            y="symbol",
            orientation="h",
            title="Total Trades"
        )


        fig.update_layout(
            xaxis_title="Total Trades",
            yaxis_title="Cryptocurrency"
        )


        st.plotly_chart(
            fig,
            width="stretch"
        )


        # ------------------------------------------------
        # VOLATILITY
        # ------------------------------------------------

        volatility_results = get_volatility(
            connection
        )


        volatility_df = pd.DataFrame(
            volatility_results,
            columns=[
                "symbol",
                "price_range",
                "price_range_percent"
            ]
        )


        st.subheader(
            "Price Volatility by Cryptocurrency"
        )


        volatility_chart_df = volatility_df.sort_values(
            "price_range_percent",
            ascending=True
        )


        fig = px.bar(
            volatility_chart_df,
            x="price_range_percent",
            y="symbol",
            orientation="h",
            title="Price Range (%)"
        )


        fig.update_layout(
            xaxis_title="Price Range (%)",
            yaxis_title="Cryptocurrency"
        )


        st.plotly_chart(
            fig,
            width="stretch"
        )


        # ------------------------------------------------
        # HOURLY TRADING VOLUME
        # ------------------------------------------------

        hourly_volume_results = get_hourly_volume(
            connection
        )


        hourly_volume_df = pd.DataFrame(
            hourly_volume_results,
            columns=[
                "hour",
                "total_volume"
            ]
        )


        st.subheader(
            "Trading Volume Over Time"
        )


        fig = px.line(
            hourly_volume_df,
            x="hour",
            y="total_volume",
            title="Hourly Trading Volume"
        )


        fig.update_layout(
            xaxis_title="Hour",
            yaxis_title="Total Volume"
        )


        st.plotly_chart(
            fig,
            width="stretch"
        )


    finally:
        connection.close()


live_dashboard()