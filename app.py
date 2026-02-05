import streamlit as st
import json
import os
from yfinance import Search

from data import (
    fetch_prices,
    stock_statistics,
    compute_portfolio
)

from charts import (
    compare_price_chart,
    correlation_heatmap,
    portfolio_chart
)

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Stock Portfolio Analyzer", layout="wide")
st.title("📊 Stock Portfolio Analyzer")

# --------------------------------------------------
# PERSISTENCE FILE
# --------------------------------------------------
DATA_FILE = "custom_companies.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        persisted_companies = json.load(f)
else:
    persisted_companies = {}

# --------------------------------------------------
# SESSION STATE INIT
# --------------------------------------------------
if "global_companies" not in st.session_state:
    st.session_state.global_companies = persisted_companies

if "selected_companies" not in st.session_state:
    st.session_state.selected_companies = []

# --------------------------------------------------
# SECTOR → COMPANY MAP
# --------------------------------------------------
SECTOR_COMPANIES = {
    "Technology": {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Google": "GOOGL",
        "Amazon": "AMZN",
        "Meta": "META"
    },
    "Finance": {
        "JPMorgan Chase": "JPM",
        "Goldman Sachs": "GS",
        "Bank of America": "BAC",
        "HDFC Bank": "HDFCBANK.NS"
    },
    "Healthcare": {
        "Pfizer": "PFE",
        "Johnson & Johnson": "JNJ",
        "Sun Pharma": "SUNPHARMA.NS"
    },
    "Consumer": {
        "Coca-Cola": "KO",
        "PepsiCo": "PEP",
        "Walmart": "WMT"
    },
    "Energy": {
        "Exxon Mobil": "XOM",
        "Chevron": "CVX",
        "Reliance": "RELIANCE.NS"
    },
    "Automotive": {
        "Tesla": "TSLA",
        "Ford": "F",
        "BMW": "BMW.DE",
        "Toyota": "TM"
    },
    "Industrial": {
        "Boeing": "BA",
        "Caterpillar": "CAT",
        "Siemens": "SIE.DE"
    },
    "Telecom": {
        "AT&T": "T",
        "Verizon": "VZ",
        "Bharti Airtel": "BHARTIARTL.NS"
    }
}

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.header("Controls")

sector = st.sidebar.selectbox(
    "Sector",
    list(SECTOR_COMPANIES.keys())
)

# Merge static + persisted searched companies
merged_companies = {
    **SECTOR_COMPANIES[sector],
    **st.session_state.global_companies
}

companies = st.sidebar.multiselect(
    "Select Companies",
    list(merged_companies.keys()),
    default=st.session_state.selected_companies
)

st.session_state.selected_companies = companies

# --------------------------------------------------
# SEARCH + ADD COMPANY (FORM = ONE CLICK)
# --------------------------------------------------
with st.sidebar.form("add_company_form"):
    search_name = st.text_input("Search Any Company (Yahoo Finance)")
    add_clicked = st.form_submit_button("Add Company")

    if add_clicked and search_name:
        result = Search(search_name, max_results=1).quotes

        if result:
            name = result[0].get("shortname", search_name)
            ticker = result[0]["symbol"]

            st.session_state.global_companies[name] = ticker

            # persist to file
            with open(DATA_FILE, "w") as f:
                json.dump(st.session_state.global_companies, f, indent=4)

            if name not in st.session_state.selected_companies:
                st.session_state.selected_companies.append(name)

            st.success(f"Added {name} ({ticker})")

        else:
            st.error("Company not found")

# --------------------------------------------------
# DATE RANGE
# --------------------------------------------------
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

# Resolve tickers
tickers = [
    merged_companies[c]
    for c in st.session_state.selected_companies
    if c in merged_companies
]

tickers = list(set(tickers))

if not tickers:
    st.warning("Please select or add at least one stock.")
    st.stop()

# --------------------------------------------------
# DATA FETCH
# --------------------------------------------------
prices = fetch_prices(tickers, start_date, end_date)

# --------------------------------------------------
# TABS
# --------------------------------------------------
tabs = st.tabs(["📈 Charts", "📊 Statistics", "💼 Portfolio"])

# ------------------ CHARTS ------------------
with tabs[0]:
    st.subheader("Stock Price Comparison")

    st.plotly_chart(
        compare_price_chart(prices, tickers),
        use_container_width=True
    )

    st.subheader("Correlation Heatmap")
    st.plotly_chart(
        correlation_heatmap(prices),
        use_container_width=True
    )

# ------------------ STATS ------------------
with tabs[1]:
    st.subheader("Stock Statistics")
    stats_df = stock_statistics(prices)
    st.dataframe(stats_df, use_container_width=True)

# ------------------ PORTFOLIO ------------------
with tabs[2]:
    st.subheader("Portfolio Construction")

    weights = []
    for t in tickers:
        w = st.slider(
            f"Weight for {t}",
            0.0,
            1.0,
            1 / len(tickers),
            0.01
        )
        weights.append(w)

    if sum(weights) == 0:
        st.error("Portfolio weights cannot be zero.")
        st.stop()

    weights = [w / sum(weights) for w in weights]

    portfolio_stats, portfolio_returns = compute_portfolio(prices, weights)

    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Daily Return", round(portfolio_stats["Avg Daily Return"], 4))
    c2.metric("Volatility", round(portfolio_stats["Volatility"], 4))
    c3.metric("Sharpe Ratio", round(portfolio_stats["Sharpe Ratio"], 4))

    st.plotly_chart(
        portfolio_chart(portfolio_returns),
        use_container_width=True
    )
