import yfinance as yf
import pandas as pd
import numpy as np
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
def fetch_prices(tickers, start, end):
    data = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False
    )
    return data["Close"]

def compute_statistics(price_df, risk_free_rate=0.06):
    returns = np.log(price_df / price_df.shift(1)).dropna()

    avg_return = returns.mean()
    volatility = returns.std()

    rf_daily = risk_free_rate / 252
    sharpe = (avg_return - rf_daily) / volatility

    stats = pd.DataFrame({
        "Avg Daily Return": avg_return,
        "Volatility": volatility,
        "Sharpe Ratio": sharpe
    })

    return stats.round(4)

def compute_portfolio(price_df, weights):
    returns = np.log(price_df / price_df.shift(1)).dropna()

    weight_array = np.array(weights)
    portfolio_returns = returns.dot(weight_array)

    avg_return = portfolio_returns.mean()
    volatility = portfolio_returns.std()
    sharpe = avg_return / volatility

    return {
        "Avg Daily Return": avg_return,
        "Volatility": volatility,
        "Sharpe Ratio": sharpe
    }, portfolio_returns
