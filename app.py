import streamlit as st
import json
import os
from yfinance import Search
from config import MARKETS
from data import fetch_prices, stock_statistics, compute_portfolio
from charts import compare_price_chart, correlation_heatmap, portfolio_chart
import plotly.express as px
import pandas as pd
# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Stock Portfolio Analyzer", layout="wide")
st.title("📊 Stock Portfolio Analyzer")

# -----------------------------
# PERSISTENCE FILE
# -----------------------------
DATA_FILE = "custom_companies.json"
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        persisted_companies = json.load(f)
else:
    persisted_companies = {}

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "global_companies" not in st.session_state:
    st.session_state.global_companies = persisted_companies
if "selected_companies" not in st.session_state:
    st.session_state.selected_companies = []
if "selected_market" not in st.session_state:
    st.session_state.selected_market = list(MARKETS.keys())[0]

# -----------------------------
# SIDEBAR CONTROLS
# -----------------------------
# 1️⃣ Market selection
market = st.sidebar.selectbox(
    "Select Market",
    list(MARKETS.keys()),
    index=list(MARKETS.keys()).index(st.session_state.selected_market)
)
st.session_state.selected_market = market

# 2️⃣ Sector selection
SECTOR_COMPANIES = MARKETS[market]
sector = st.sidebar.selectbox(
    "Select Sector",
    list(SECTOR_COMPANIES.keys())
)

# -----------------------------
# 3️⃣ Merge companies for dropdown
# -----------------------------
# Start with static companies in sector
merged_companies = dict(SECTOR_COMPANIES[sector])

# Add previously added companies only if they belong to this market & sector
for name, info in st.session_state.global_companies.items():
    if isinstance(info, dict):
        # If structured as {"ticker": ..., "market": ..., "sector": ...}
        if info.get("market") == market and info.get("sector") == sector:
            merged_companies[name] = info["ticker"]
    else:
        # fallback for older format (just ticker string)
        merged_companies[name] = info

# 4️⃣ Company selection
companies = st.sidebar.multiselect(
    "Select Companies",
    list(merged_companies.keys()),
    default=st.session_state.selected_companies
)
st.session_state.selected_companies = companies

# -----------------------------
# 5️⃣ Add new company by name with Yahoo fallback
# -----------------------------
with st.sidebar.form("add_company_form"):
    search_name = st.text_input("Add Company")
    add_clicked = st.form_submit_button("Add Company")

    if add_clicked and search_name:
        # Flatten all companies
        all_companies_flat = {}
        for sector_dict in MARKETS[market].values():
            all_companies_flat.update(sector_dict)
        for name, info in st.session_state.global_companies.items():
            if isinstance(info, dict):
                all_companies_flat[name] = info["ticker"]
            else:
                all_companies_flat[name] = info

        if search_name in all_companies_flat:
            ticker = all_companies_flat[search_name]
            st.success(f"Added {search_name} ({ticker})")
        else:
            # Yahoo Finance search fallback
            result = Search(search_name, max_results=1).quotes
            if result:
                name = result[0].get("shortname", search_name)
                ticker = result[0]["symbol"]
                st.success(f"Added {name} ({ticker})")
            else:
                st.error("Company not found.")
                name = None
                ticker = None

        # Save to JSON with market & sector
        if name and ticker:
            st.session_state.global_companies[name] = {
                "ticker": ticker,
                "market": market,
                "sector": sector
            }
            with open(DATA_FILE, "w") as f:
                json.dump(st.session_state.global_companies, f, indent=4)

            # Add to selected companies
            if name not in st.session_state.selected_companies:
                st.session_state.selected_companies.append(name)

# -----------------------------
# DATE RANGE
# -----------------------------
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

# -----------------------------
# RESOLVE TICKERS
# -----------------------------
tickers = [
    merged_companies.get(c) if c in merged_companies else st.session_state.global_companies.get(c, {}).get("ticker")
    for c in st.session_state.selected_companies
]
tickers = list(set([t for t in tickers if t]))  # remove None

if not tickers:
    st.warning("Select or add stock.")
    st.stop()

# -----------------------------
# FETCH DATA
# -----------------------------
prices = fetch_prices(tickers, start_date, end_date)

# -----------------------------
# RENAME COLUMNS TO COMPANY NAMES & HANDLE MISSING DATA
# -----------------------------
ticker_to_name = {}
for k, v in {**SECTOR_COMPANIES[sector], **st.session_state.global_companies}.items():
    if isinstance(v, dict):
        ticker_to_name[v["ticker"]] = k
    else:
        ticker_to_name[v] = k

prices_named = prices.rename(columns=ticker_to_name)
prices_named = prices_named.ffill()  # forward fill missing prices

# -----------------------------
# TABS
# -----------------------------
tabs = st.tabs(["📈 Charts", "📊 Statistics", "💼 Portfolio"])

# ------------------ CHARTS ------------------
with tabs[0]:
    st.subheader("Stock Price Comparison")

    chart_stocks = st.multiselect(
        "Select stocks to display in charts",
        list(prices_named.columns),
        default=list(prices_named.columns)
    )

    st.plotly_chart(
        compare_price_chart(prices_named[chart_stocks], chart_stocks),
        use_container_width=True
    )

    st.subheader("Correlation Heatmap")
    st.plotly_chart(
        correlation_heatmap(prices_named[chart_stocks]),
        use_container_width=True
    )

# ------------------ STATISTICS ------------------
with tabs[1]:
    st.subheader("Stock Statistics")
    stats_df = stock_statistics(prices_named)
    st.dataframe(stats_df, use_container_width=True)

    st.markdown("---")
    st.subheader("Bar Chart Comparison")
    metric = st.selectbox(
        "Select metric to display as bar chart",
        stats_df.columns.drop("Company")  # exclude the company column
    )
    from charts import statistics_bar_chart
    st.plotly_chart(statistics_bar_chart(stats_df, metric), use_container_width=True)

    st.markdown("---")
    st.subheader("Daily Returns Histogram")
    from charts import daily_returns_histogram

    company_for_hist = st.selectbox(
        "Select company for daily returns histogram",
        stats_df["Company"]
    )
    st.plotly_chart(daily_returns_histogram(prices_named, company_for_hist), use_container_width=True)
# ------------------ PORTFOLIO ------------------
with tabs[2]:
    st.subheader("Portfolio Construction")

    # Columns: right first to make chart slightly higher
    right_col, left_col = st.columns([1, 2])

    # Placeholder for the pie chart
    pie_placeholder = right_col.empty()

    # 1️⃣ Sliders for weights
    weights = []
    with left_col:
        for t in prices_named.columns:
            w = st.slider(
                f"{t}",
                0.0,
                1.0,
                1 / len(prices_named.columns),
                0.01,
                key=f"slider_{t}"  # unique key for each slider
            )
            weights.append(w)

        if sum(weights) == 0:
            st.error("Portfolio weights cannot be zero.")
            st.stop()

        weights = [w / sum(weights) for w in weights]  # normalize

    # 2️⃣ Pie chart updated dynamically
    weights_df = pd.DataFrame({
        "Company": prices_named.columns,
        "Weight": weights
    })

    fig = px.pie(weights_df, names="Company", values="Weight", hole=0.4)
    pie_placeholder.plotly_chart(fig, use_container_width=True)  # only once

    # 3️⃣ Compute portfolio stats
    portfolio_stats, portfolio_returns = compute_portfolio(prices_named, weights)

    # 4️⃣ Show metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Daily Return", round(portfolio_stats["Avg Daily Return"], 4))
    c2.metric("Volatility", round(portfolio_stats["Volatility"], 4))
    c3.metric("Sharpe Ratio", round(portfolio_stats["Sharpe Ratio"], 4))

    # 5️⃣ Portfolio cumulative returns chart
    st.subheader("Portfolio Cumulative Returns")
    st.plotly_chart(
        portfolio_chart(portfolio_returns),
        use_container_width=True
    )
