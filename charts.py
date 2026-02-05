import plotly.express as px

def compare_price_chart(price_df, selected):
    data = price_df[selected].reset_index()
    return px.line(
        data,
        x="Date",
        y=selected,
        title="Stock Price Comparison"
    )

def correlation_heatmap(price_df):
    returns = price_df.pct_change().dropna()
    return px.imshow(
        returns.corr(),
        color_continuous_scale="RdYlGn",
        title="Stock Return Correlation"
    )

def portfolio_chart(portfolio_returns):
    cum = (1 + portfolio_returns).cumprod()
    return px.line(cum, title="Portfolio Cumulative Returns")
