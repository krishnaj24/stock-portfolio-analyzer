import plotly.express as px
import pandas as pd

def price_chart(df, ticker):
    data = df[ticker].reset_index()
    fig = px.line(
        data,
        x="Date",
        y="Close",
        title=f"{ticker} Price Trend"
    )
    return fig


def heatmap_chart(df, tickers):
    latest = []

    for t in tickers:
        change = (
            df[t]["Close"].iloc[-1] - df[t]["Close"].iloc[0]
        ) / df[t]["Close"].iloc[0] * 100
        latest.append({"Ticker": t, "Change %": change})

    heat_df = pd.DataFrame(latest)

    fig = px.imshow(
        heat_df.set_index("Ticker"),
        color_continuous_scale="RdYlGn",
        title="Sector Performance Heatmap"
    )
    return fig
