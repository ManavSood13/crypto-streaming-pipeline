from datetime import datetime, timezone

import streamlit as st


# A candle is only expected every 10 seconds, so allow a little slack
# before calling the stream stale.
FRESH_SECONDS = 30
STALE_SECONDS = 120


def _card(title, value):
    return (
        '<div class="status-card">'
        f'<div class="status-title">{title}</div>'
        f'<div class="status-value">{value}</div>'
        '</div>'
    )


def _freshness(latest_bucket):
    """
    Describe how recently the pipeline wrote a candle.
    """

    if latest_bucket is None:
        return "🔴 No data", None

    age = (
        datetime.now(timezone.utc) - latest_bucket
    ).total_seconds()

    if age <= FRESH_SECONDS:
        return "🟢 Live", age

    if age <= STALE_SECONDS:
        return "🟡 Lagging", age

    return "🔴 Stale", age


def render_pipeline_status(health=None, connected=True):
    """
    Show real pipeline health.

    The previous version hard coded three green indicators, so the panel
    reported everything as healthy even with the ingester stopped.
    """

    st.subheader(
        "Pipeline Status"
    )

    latest_bucket, candles_last_minute = (
        health if health else (None, 0)
    )

    ingestion, age = _freshness(latest_bucket)

    status_col1, status_col2, status_col3 = st.columns(
        3,
        gap="medium"
    )

    with status_col1:

        st.markdown(
            _card(
                "Database",
                "🟢 Connected" if connected else "🔴 Disconnected"
            ),
            unsafe_allow_html=True
        )

    with status_col2:

        st.markdown(
            _card(
                "Ingestion",
                ingestion
                if age is None
                else f"{ingestion} · {int(age)}s ago"
            ),
            unsafe_allow_html=True
        )

    with status_col3:

        st.markdown(
            _card(
                "Candles / min",
                f"{candles_last_minute or 0}"
            ),
            unsafe_allow_html=True
        )


def render_footer():

    st.markdown(
        '<div class="dashboard-footer">Crypto Streaming Pipeline<br>'
        'Binance WebSocket • PostgreSQL • Pandas • Streamlit</div>',
        unsafe_allow_html=True
    )
