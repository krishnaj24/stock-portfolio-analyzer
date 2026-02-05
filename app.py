import streamlit as st
from data import fetch_prices, compute_statistics, compute_portfolio
from charts import stock_price_chart, portfolio_chart

st.set_page_config(layout="wide")
st.title("📊 Stock Portfolio Analyzer")

# ---- SIDEBAR ----
st.sidebar.header("Controls")

tickers = st.sidebar.multiselect(
    "Add stocks to watchlist",
    ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "F", "BMW.DE"]
)

start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

tabs = st.tabs(["📈 Overview", "📊 Statistics", "💼 Portfolio"])

if len(tickers) == 0:
    st.warning("Add stocks to watchlist")
    st.stop()

prices = fetch_prices(tickers, start_date, end_date)

# ---- OVERVIEW TAB ----
with tabs[0]:
    stock = st.selectbox("Select stock", tickers)
    st.plotly_chart(stock_price_chart(prices, stock), use_container_width=True)

# ---- STATISTICS TAB ----
with tabs[1]:
    stats = compute_statistics(prices)
    st.dataframe(stats)

# ---- PORTFOLIO TAB ----
with tabs[2]:
    st.subheader("Portfolio Weights")

    weights = []
    for t in tickers:
        w = st.slider(f"{t} weight", 0.0, 1.0, 1/len(tickers))
        weights.append(w)

    if sum(weights) == 0:
        st.error("Weights cannot be zero")
        st.stop()

    weights = [w / sum(weights) for w in weights]

    portfolio_stats, portfolio_returns = compute_portfolio(prices, weights)

    st.metric("Avg Daily Return", round(portfolio_stats["Avg Daily Return"], 4))
    st.metric("Volatility", round(portfolio_stats["Volatility"], 4))
    st.metric("Sharpe Ratio", round(portfolio_stats["Sharpe Ratio"], 4))

    st.plotly_chart(
        portfolio_chart(portfolio_returns),
        use_container_width=True
    )
