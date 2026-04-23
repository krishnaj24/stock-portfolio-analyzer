from ai_utils import ask_ai

def explain_price_chart(stocks, start, end, stats_df):
    prompt = f"""
    Stock performance analysis.

    Stocks: {stocks}
    Period: {start} to {end}
    Statistics:
    {stats_df.to_string()}

    Explain the trend in simple language.
    Start with one word sentiment:
    POSITIVE / NEGATIVE / NEUTRAL
    """
    return ask_ai(prompt)

def explain_heatmap(stocks):
    prompt = f"""
    Explain stock correlation in simple words.
    Stocks: {stocks}
    Why diversification matters?
    """
    return ask_ai(prompt)

def explain_statistics(stats):
    prompt = f"""
    Explain these stock statistics in simple terms:
    {stats}
    Which stock looks strongest and weakest?
    """
    return ask_ai(prompt)