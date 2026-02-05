import yfinance as yf
import pandas as pd

SECTOR_TICKERS = {
    "IT": ["TCS.NS", "INFY.NS", "WIPRO.NS"],
    "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"],
    "Pharma": ["SUNPHARMA.NS", "DRREDDY.NS"],
    "Energy": ["RELIANCE.NS", "ONGC.NS"]
}

def fetch_stock_data(tickers, period):
    data = yf.download(
        tickers,
        period=period,
        group_by="ticker",
        auto_adjust=True,
        progress=False
    )
    return data
