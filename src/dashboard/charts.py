import plotly.express as px

from src.dashboard.theme import direction_colors


def create_volume_chart(
    volume_df
):
    chart_df = volume_df.sort_values(
        "total_volume",
        ascending=True
    )

    figure = px.bar(
        chart_df,
        x="total_volume",
        y="symbol",
        orientation="h",
        title="Trading Volume"
    )

    figure.update_layout(
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

    return figure


def create_performance_chart(
    price_change_df
):
    chart_df = price_change_df.sort_values(
        "price_change_percent",
        ascending=True
    )

    figure = px.bar(
        chart_df,
        x="price_change_percent",
        y="symbol",
        orientation="h",
        title="Price Performance"
    )

    # Green for gainers, red for losers.
    figure.update_traces(
        marker_color=direction_colors(
            chart_df["price_change_percent"]
        )
    )

    figure.update_layout(
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

    return figure


def create_activity_chart(
    trading_activity_df
):
    chart_df = trading_activity_df.sort_values(
        "total_trades",
        ascending=True
    )

    figure = px.bar(
        chart_df,
        x="total_trades",
        y="symbol",
        orientation="h",
        title="Trading Activity"
    )

    figure.update_layout(
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

    return figure


def create_volatility_chart(
    volatility_df
):
    chart_df = volatility_df.sort_values(
        "price_range_percent",
        ascending=True
    )

    figure = px.bar(
        chart_df,
        x="price_range_percent",
        y="symbol",
        orientation="h",
        title="Price Volatility"
    )

    figure.update_layout(
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

    return figure


def create_volume_over_time_chart(
    volume_over_time_df
):
    """
    Line chart of traded volume over time.

    Markers are always drawn: with a short history the series can hold a
    single point, and a line alone renders nothing at all.
    """

    figure = px.line(
        volume_over_time_df,
        x="bucket_time",
        y="total_volume",
        title="Trading Volume Over Time",
        markers=True
    )

    figure.update_layout(
        xaxis_title="Time",
        yaxis_title="Total Volume",
        height=420,
        margin=dict(
            l=10,
            r=10,
            t=50,
            b=10
        )
    )

    return figure
