import plotly.express as px
import pandas as pd
import numpy as np
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
    corr=returns.corr()
    fig = px.imshow(
            corr,
            color_continuous_scale="RdYlGn",
            text_auto=True,
            title="Stock Return Correlation",
        )
        # Update axis labels to show "Company" instead of "Ticker"
    fig.update_xaxes(title_text="Company")
    fig.update_yaxes(title_text="Company")        
    return fig

def portfolio_chart(portfolio_returns):
    cum = (1 + portfolio_returns).cumprod()
    df = pd.DataFrame({"Cumulative Return": cum})
    return px.line(
        df,y="Cumulative Return",title="Portfolio Cumulative Returns"
    )
# ------------------ New Charts ------------------

def statistics_bar_chart(stats_df, column):
    """Bar chart comparing companies for a selected metric"""
    import plotly.express as px

    if column not in stats_df.columns:
        return None

    fig = px.bar(
        stats_df,
        x="Company",
        y=column,
        title=f"{column} Comparison",
        text=column,
        color=column,
        color_continuous_scale="Viridis"
    )
    fig.update_layout(yaxis_title=column, xaxis_title="Company")
    return fig

def daily_returns_histogram(price_df, selected_company):
    """Histogram of daily returns for a single company"""
    if selected_company not in price_df.columns:
        return None

    returns = np.log(price_df[selected_company] / price_df[selected_company].shift(1)).dropna()
    fig = px.histogram(
        returns,
        nbins=50,
        title=f"Daily Returns Distribution: {selected_company}",
        labels={"value": "Daily Log Return"},
        #marginal="box"
    )
    return fig
