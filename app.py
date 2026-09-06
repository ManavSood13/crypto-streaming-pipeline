import streamlit as st

from src.dashboard.components import (
    load_css,
    render_header,
    render_dashboard
)

from src.dashboard.data import (
    get_dashboard_data
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

load_css()


# ------------------------------------------------
# DASHBOARD HEADER
# ------------------------------------------------

render_header()


# ------------------------------------------------
# LIVE DASHBOARD
# ------------------------------------------------

@st.fragment(
    run_every="3s"
)
def live_dashboard():

    # The connection is cached and shared across reruns, so it must
    # not be closed here.
    render_dashboard(
        get_dashboard_data()
    )


# ------------------------------------------------
# RUN DASHBOARD
# ------------------------------------------------

live_dashboard()