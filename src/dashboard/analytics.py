import streamlit as st

from src.dashboard.charts import (
    create_volume_chart,
    create_performance_chart,
    create_activity_chart,
    create_volatility_chart,
    create_hourly_volume_chart
)


def render_market_analytics(
    volume_df,
    price_change_df,
    trading_activity_df,
    volatility_df
):

    st.subheader(
        "Market Analytics"
    )

    volume_fig = create_volume_chart(
        volume_df
    )

    performance_fig = create_performance_chart(
        price_change_df
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

    activity_fig = create_activity_chart(
        trading_activity_df
    )

    volatility_fig = create_volatility_chart(
        volatility_df
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


def render_hourly_volume(
    hourly_volume_df
):

    st.subheader(
        "Trading Volume Over Time"
    )

    hourly_fig = create_hourly_volume_chart(
        hourly_volume_df
    )

    st.plotly_chart(
        hourly_fig,
        width="stretch"
    )