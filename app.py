import streamlit as st
from data import SECTOR_TICKERS, fetch_stock_data
from charts import price_chart, heatmap_chart

st.set_page_config(layout="wide")
st.title("📈 Stock Market Dashboard")

# Sidebar
st.sidebar.header("Controls")

sector = st.sidebar.selectbox(
    "Select Sector",
    list(SECTOR_TICKERS.keys())
)

period = st.sidebar.selectbox(
    "Select Time Period",
    ["1mo", "3mo", "6mo", "1y", "5y"]
)

tickers = SECTOR_TICKERS[sector]

search_ticker = st.sidebar.selectbox(
    "Search Stock",
    tickers
)

# Fetch data
data = fetch_stock_data(tickers, period)

# Layout
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        price_chart(data, search_ticker),
        use_container_width=True
    )

with col2:
    st.plotly_chart(
        heatmap_chart(data, tickers),
        use_container_width=True
    )
