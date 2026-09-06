import streamlit as st

from src.dashboard.safe import (
    lookup,
    first_row,
    money,
    percent
)


def render_header():

    header_col1, header_col2 = st.columns(
        [5, 1]
    )

    with header_col1:

        st.title(
            "₿ Crypto Streaming Pipeline"
        )

        st.caption(
            "Real-Time Cryptocurrency Market Dashboard"
        )

    with header_col2:

        st.markdown(
            '<div class="live-badge">● LIVE</div>',
            unsafe_allow_html=True
        )


def render_kpis(
    latest_df,
    price_change_df,
    volume_df,
    total_candles
):

    btc_price = lookup(latest_df, "BTCUSDT", "latest_price")
    eth_price = lookup(latest_df, "ETHUSDT", "latest_price")

    btc_change = lookup(
        price_change_df,
        "BTCUSDT",
        "price_change_percent"
    )

    eth_change = lookup(
        price_change_df,
        "ETHUSDT",
        "price_change_percent"
    )

    top_volume_symbol = first_row(volume_df, "symbol", "—")
    top_volume = first_row(volume_df, "total_volume")

    col1, col2, col3, col4 = st.columns(
        4,
        gap="medium"
    )

    with col1:

        st.metric(
            label="BTC Price",
            value=money(btc_price),
            delta=percent(btc_change),
            icon="🪙",
            border=True
        )

    with col2:

        st.metric(
            label="ETH Price",
            value=money(eth_price),
            delta=percent(eth_change),
            icon="💎",
            border=True
        )

    with col3:

        st.metric(
            label="Top Volume",
            value=top_volume_symbol,
            delta=None if top_volume is None else f"{top_volume:,.2f}",
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


def render_market_overview(
    latest_df,
    price_change_df
):

    st.subheader(
        "Market Overview"
    )

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

            "Symbol":
                st.column_config.TextColumn(
                    "Symbol"
                ),

            "Latest Price":
                st.column_config.NumberColumn(
                    "Latest Price",
                    format="$%.2f"
                ),

            "Change %":
                st.column_config.NumberColumn(
                    "Change %",
                    format="%.2f%%"
                ),

            "Last Update":
                st.column_config.DatetimeColumn(
                    "Last Update",
                    format="HH:mm:ss"
                )
        }
    )