import plotly.express as px


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


def create_hourly_volume_chart(
    hourly_volume_df
):
    figure = px.line(
        hourly_volume_df,
        x="hour",
        y="total_volume",
        title="Hourly Trading Volume"
    )

    figure.update_layout(
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

    return figure