import streamlit as st
import plotly.express as px
import pandas as pd
from pathlib import Path

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


# ------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------

st.set_page_config(
    page_title="Crypto Streaming Pipeline",
    page_icon="🪙",
    layout="wide"
)


# ------------------------------------------------
# LOAD CSS
# ------------------------------------------------

css_path = Path("assets/style.css")

with open(css_path) as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )


# ------------------------------------------------
# DASHBOARD HEADER
# ------------------------------------------------

header_col1, header_col2 = st.columns([5, 1])

with header_col1:
    st.title("₿ Crypto Streaming Pipeline")
    st.caption(
        "Real-Time Cryptocurrency Market Dashboard"
    )

with header_col2:
    st.markdown(
        '<div class="live-badge">● LIVE</div>',
        unsafe_allow_html=True
    )


# ------------------------------------------------
# LIVE DASHBOARD
# ------------------------------------------------

@st.fragment(run_every="3s")
def live_dashboard():

    connection = get_connection()

    try:

        # ------------------------------------------------
        # GET LATEST PRICES
        # ------------------------------------------------

        latest_results = get_latest_prices(
            connection
        )

        latest_df = latest_prices_dataframe(
            latest_results
        )


        # ------------------------------------------------
        # GET VOLUME DATA
        # ------------------------------------------------

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


        # ------------------------------------------------
        # GET PRICE CHANGE
        # ------------------------------------------------

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


        # ------------------------------------------------
        # TOTAL CANDLES
        # ------------------------------------------------

        total_candles = get_total_candles(
            connection
        )


        # =================================================
        # KPI CARDS
        # =================================================

        btc_price = latest_df.loc[
            latest_df["symbol"] == "BTCUSDT",
            "latest_price"
        ].iloc[0]

        eth_price = latest_df.loc[
            latest_df["symbol"] == "ETHUSDT",
            "latest_price"
        ].iloc[0]

        btc_change = price_change_df.loc[
            price_change_df["symbol"] == "BTCUSDT",
            "price_change_percent"
        ].iloc[0]

        eth_change = price_change_df.loc[
            price_change_df["symbol"] == "ETHUSDT",
            "price_change_percent"
        ].iloc[0]

        top_volume_symbol = volume_results[0][0]

        top_volume = volume_df.loc[
            volume_df["symbol"] == top_volume_symbol,
            "total_volume"
        ].iloc[0]


        col1, col2, col3, col4 = st.columns(
            4,
            gap="medium"
        )

        with col1:
            st.metric(
                label="BTC Price",
                value=f"${btc_price:,.2f}",
                delta=f"{btc_change:+.2f}%",
                icon="🪙",
                border=True
            )

        with col2:
            st.metric(
                label="ETH Price",
                value=f"${eth_price:,.2f}",
                delta=f"{eth_change:+.2f}%",
                icon="💎",
                border=True
            )

        with col3:
            st.metric(
                label="Top Volume",
                value=top_volume_symbol,
                delta=f"{top_volume:,.2f}",
                delta_color="off",
                icon="📊",
                border=True
            )

        with col4:
            st.metric(
                label="Total Candles",
                value=f"{total_candles:,}",
                icon="📈",
                border=True
            )


        st.markdown("---")


        # =================================================
        # MARKET OVERVIEW
        # =================================================

        st.subheader("Market Overview")

        market_df = latest_df.copy()

        market_df = market_df.merge(
            price_change_df[
                [
                    "symbol",
                    "price_change_percent"
                ]
            ],
            on="symbol",
            how="left"
        )

        market_df = market_df[
            [
                "symbol",
                "latest_price",
                "price_change_percent",
                "bucket_start"
            ]
        ]

        market_df.columns = [
            "Symbol",
            "Latest Price",
            "Change %",
            "Last Update"
        ]

        st.dataframe(
            market_df,
            width="stretch",
            hide_index=True,
            column_config={
                "Symbol": st.column_config.TextColumn(
                    "Symbol"
                ),
                "Latest Price": st.column_config.NumberColumn(
                    "Latest Price",
                    format="$%.2f"
                ),
                "Change %": st.column_config.NumberColumn(
                    "Change %",
                    format="%.2f%%"
                ),
                "Last Update": st.column_config.DatetimeColumn(
                    "Last Update",
                    format="HH:mm:ss"
                )
            }
        )


        # =================================================
        # PRICE ANALYSIS
        # =================================================

        st.subheader("Price Analysis")

        selector_col, timeframe_col = st.columns(
            [3, 1],
            gap="medium"
        )

        symbols = latest_df[
            "symbol"
        ].tolist()

        with selector_col:
            selected_symbol = st.selectbox(
                "Cryptocurrency",
                symbols,
                label_visibility="visible"
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


        # ------------------------------------------------
        # PRICE HISTORY
        # ------------------------------------------------

        history_results = get_price_history(
            connection,
            selected_symbol,
            history_limit
        )

        history_df = price_history_dataframe(
            history_results
        )

        selected_price = latest_df.loc[
            latest_df["symbol"] == selected_symbol,
            "latest_price"
        ].iloc[0]

        selected_change = price_change_df.loc[
            price_change_df["symbol"] == selected_symbol,
            "price_change_percent"
        ].iloc[0]


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
                f"${selected_price:,.2f}",
                delta=f"{selected_change:+.2f}%"
            )


        st.line_chart(
            history_df,
            x="bucket_start",
            y="close",
            width="stretch"
        )


        # =================================================
        # MARKET ANALYTICS
        # =================================================

        st.subheader("Market Analytics")


        # ------------------------------------------------
        # TRADING VOLUME
        # ------------------------------------------------

        volume_chart_df = volume_df.sort_values(
            "total_volume",
            ascending=True
        )

        volume_fig = px.bar(
            volume_chart_df,
            x="total_volume",
            y="symbol",
            orientation="h",
            title="Trading Volume"
        )

        volume_fig.update_layout(
            xaxis_title="Total Volume",
            yaxis_title="",
            height=420,
            margin=dict(
                l=10,
                r=10,
                t=50,
                b=10
            )
        )


        # ------------------------------------------------
        # PRICE PERFORMANCE
        # ------------------------------------------------

        price_change_chart_df = price_change_df.sort_values(
            "price_change_percent",
            ascending=True
        )

        performance_fig = px.bar(
            price_change_chart_df,
            x="price_change_percent",
            y="symbol",
            orientation="h",
            title="Price Performance"
        )

        performance_fig.update_layout(
            xaxis_title="Price Change (%)",
            yaxis_title="",
            height=420,
            margin=dict(
                l=10,
                r=10,
                t=50,
                b=10
            )
        )


        analytics_col1, analytics_col2 = st.columns(
            2,
            gap="medium"
        )

        with analytics_col1:
            st.plotly_chart(
                volume_fig,
                width="stretch"
            )

        with analytics_col2:
            st.plotly_chart(
                performance_fig,
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

        trading_activity_chart_df = (
            trading_activity_df
            .sort_values(
                "total_trades",
                ascending=True
            )
        )

        activity_fig = px.bar(
            trading_activity_chart_df,
            x="total_trades",
            y="symbol",
            orientation="h",
            title="Trading Activity"
        )

        activity_fig.update_layout(
            xaxis_title="Total Trades",
            yaxis_title="",
            height=420,
            margin=dict(
                l=10,
                r=10,
                t=50,
                b=10
            )
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

        volatility_chart_df = (
            volatility_df
            .sort_values(
                "price_range_percent",
                ascending=True
            )
        )

        volatility_fig = px.bar(
            volatility_chart_df,
            x="price_range_percent",
            y="symbol",
            orientation="h",
            title="Price Volatility"
        )

        volatility_fig.update_layout(
            xaxis_title="Price Range (%)",
            yaxis_title="",
            height=420,
            margin=dict(
                l=10,
                r=10,
                t=50,
                b=10
            )
        )


        analytics_col3, analytics_col4 = st.columns(
            2,
            gap="medium"
        )

        with analytics_col3:
            st.plotly_chart(
                activity_fig,
                width="stretch"
            )

        with analytics_col4:
            st.plotly_chart(
                volatility_fig,
                width="stretch"
            )


        # =================================================
        # TRADING VOLUME OVER TIME
        # =================================================

        st.subheader("Trading Volume Over Time")

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

        hourly_fig = px.line(
            hourly_volume_df,
            x="hour",
            y="total_volume",
            title="Hourly Trading Volume"
        )

        hourly_fig.update_layout(
            xaxis_title="Hour",
            yaxis_title="Total Volume",
            height=420,
            margin=dict(
                l=10,
                r=10,
                t=50,
                b=10
            )
        )

        st.plotly_chart(
            hourly_fig,
            width="stretch"
        )


        # =================================================
        # PIPELINE STATUS
        # =================================================

        st.subheader("Pipeline Status")

        status_col1, status_col2, status_col3 = st.columns(
            3,
            gap="medium"
        )

        with status_col1:
            st.markdown(
                """
                <div class="status-card">
                    <div class="status-title">
                        Database
                    </div>
                    <div class="status-value">
                        🟢 Connected
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with status_col2:
            st.markdown(
                """
                <div class="status-card">
                    <div class="status-title">
                        Dashboard Refresh
                    </div>
                    <div class="status-value">
                        🟢 Active
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with status_col3:
            st.markdown(
                """
                <div class="status-card">
                    <div class="status-title">
                        Data Processing
                    </div>
                    <div class="status-value">
                        🟢 Active
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


        # =================================================
        # FOOTER
        # =================================================

        st.markdown(
            """
            <div class="dashboard-footer">
                Crypto Streaming Pipeline
                <br>
                Binance WebSocket • PostgreSQL • Pandas • Streamlit
            </div>
            """,
            unsafe_allow_html=True
        )


    finally:
        connection.close()


# ------------------------------------------------
# RUN DASHBOARD
# ------------------------------------------------

live_dashboard()