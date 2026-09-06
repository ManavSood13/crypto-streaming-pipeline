from pathlib import Path

import streamlit as st

from src.dashboard.overview import (
    render_header,
    render_kpis,
    render_market_overview
)

from src.dashboard.price import (
    render_price_analysis
)

from src.dashboard.analytics import (
    render_market_analytics,
    render_volume_over_time
)

from src.dashboard.status import (
    render_pipeline_status,
    render_footer
)


# Anchored to the project root so the dashboard can be launched from
# any working directory.
CSS_PATH = Path(__file__).resolve().parents[2] / "assets" / "style.css"


def load_css():
    if not CSS_PATH.exists():
        return

    st.markdown(
        f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True
    )


def render_dashboard(data):

    render_kpis(
        data["latest_df"],
        data["price_change_df"],
        data["volume_df"],
        data["total_candles"]
    )

    st.markdown("---")

    render_market_overview(
        data["latest_df"],
        data["price_change_df"]
    )

    render_price_analysis(
        data["latest_df"],
        data["price_change_df"],
        data["connection"]
    )

    render_market_analytics(
        data["volume_df"],
        data["price_change_df"],
        data["trading_activity_df"],
        data["volatility_df"]
    )

    render_volume_over_time(
        data["volume_over_time_df"]
    )

    render_pipeline_status(
        data.get("health")
    )

    render_footer()