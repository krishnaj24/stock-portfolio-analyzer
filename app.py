import streamlit as st
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

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Stock Portfolio Analyzer", layout="wide")
st.title("📊 Stock Portfolio Analyzer")

# ---------------- COMPANY MAP ----------------
COMPANY_MAP = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "Tesla": "TSLA",
    "Ford": "F",
    "BMW": "BMW.DE"
}

# ---------------- SIDEBAR ----------------
st.sidebar.header("Controls")

sector = st.sidebar.selectbox(
    "Sector",
    ["Tech", "Auto", "Mixed"]
)

companies = st.sidebar.multiselect(
    "Select Companies",
    list(COMPANY_MAP.keys())
)

search_name = st.sidebar.text_input("Search Company (Optional)")
extra_tickers = []

if search_name:
    result = Search(search_name, max_results=1).quotes
    if result:
        extra_tickers.append(result[0]["symbol"])

start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

# Resolve tickers
tickers = [COMPANY_MAP[c] for c in companies] + extra_tickers
tickers = list(set(tickers))  # remove duplicates

if len(tickers) == 0:
    st.warning("Please select or search at least one stock.")
    st.stop()

# ---------------- DATA FETCH ----------------
prices = fetch_prices(tickers, start_date, end_date)

# ---------------- TABS ----------------
tabs = st.tabs(["📈 Charts", "📊 Statistics", "💼 Portfolio"])

# ======================================================
# 📈 CHARTS TAB
# ======================================================
with tabs[0]:
    st.subheader("Stock Price Comparison")

    selected = st.multiselect(
        "Compare Stocks",
        tickers,
        default=tickers
    )

    if selected:
        st.plotly_chart(
            compare_price_chart(prices, selected),
            use_container_width=True
        )

    st.subheader("Correlation Between Stocks")
    st.plotly_chart(
        correlation_heatmap(prices),
        use_container_width=True
    )

# ======================================================
# 📊 STATISTICS TAB
# ======================================================
with tabs[1]:
    st.subheader("Stock Performance Statistics")

    stats_df = stock_statistics(prices)
    st.dataframe(stats_df, use_container_width=True)

# ======================================================
# 💼 PORTFOLIO TAB
# ======================================================
with tabs[2]:
    st.subheader("Portfolio Construction")

    weights = []
    for t in tickers:
        w = st.slider(
            f"Weight for {t}",
            min_value=0.0,
            max_value=1.0,
            value=1 / len(tickers),
            step=0.01
        )
        weights.append(w)

    if sum(weights) == 0:
        st.error("Total portfolio weight cannot be zero.")
        st.stop()

    # Normalize weights
    weights = [w / sum(weights) for w in weights]

    portfolio_stats, portfolio_returns = compute_portfolio(prices, weights)

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Daily Return", round(portfolio_stats["Avg Daily Return"], 4))
    col2.metric("Volatility", round(portfolio_stats["Volatility"], 4))
    col3.metric("Sharpe Ratio", round(portfolio_stats["Sharpe Ratio"], 4))

    st.plotly_chart(
        portfolio_chart(portfolio_returns),
        use_container_width=True
    )
