import streamlit as st
import json
import os
from yfinance import Search
from config import MARKETS
from data import fetch_prices, stock_statistics, compute_portfolio
from charts import compare_price_chart, correlation_heatmap, portfolio_chart
import plotly.express as px
import pandas as pd
import numpy as np

from ai_utils import chart_insight, ask_ai

if "insights_cache" not in st.session_state:
    st.session_state.insights_cache = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}
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
# SIDEBAR CONTROLS (NEW)
# -----------------------------

st.sidebar.header("Portfolio Universe")

# 1️⃣ MULTI MARKET SELECTION
selected_markets = st.sidebar.multiselect(
    "Select Markets",
    list(MARKETS.keys()),
    default=[]  # preselect both
)

if not selected_markets:
    st.warning("Please select at least one market")
    st.stop()

# 2️⃣ GET ALL SECTORS FROM SELECTED MARKETS
available_sectors = []
for m in selected_markets:
    available_sectors.extend(MARKETS[m].keys())

selected_sectors = st.sidebar.multiselect(
    "Select Sectors",
    sorted(list(set(available_sectors))),
    default=[]
)

if not selected_sectors:
    st.warning("Please select at least one sector")
    st.stop()

# -----------------------------
# BUILD GLOBAL COMPANY UNIVERSE
# -----------------------------
merged_companies = {}

# Add companies from config.py based on selected markets & sectors
for market in selected_markets:
    for sector, comps in MARKETS[market].items():
        if sector in selected_sectors:
            merged_companies.update(comps)

# Add custom companies (user added)
for name, info in st.session_state.global_companies.items():
    if isinstance(info, dict):
        if info.get("market") in selected_markets and info.get("sector") in selected_sectors:
            merged_companies[name] = info["ticker"]
    else:
        merged_companies[name] = info

# -----------------------------
# COMPANY MULTISELECT (GLOBAL)
# -----------------------------
companies = st.sidebar.multiselect(
    "Select Companies",
    sorted(list(merged_companies.keys())),
)
st.session_state.selected_companies = companies
# -----------------------------
# Add new company by name with Yahoo fallback
# -----------------------------
with st.sidebar.form("add_company_form"):
    search_name = st.text_input("Add Company")
    add_clicked = st.form_submit_button("Add Company")
    if add_clicked and search_name:
        # Flatten all companies
        all_companies_flat = {}
        for m in MARKETS:
            for sector_dict in MARKETS[m].values():
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
tickers = [merged_companies[c] for c in st.session_state.selected_companies if c in merged_companies]

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
ticker_to_name = {v: k for k, v in merged_companies.items()}
prices_named = prices.rename(columns=ticker_to_name)
prices_named = prices_named.dropna(axis=1, how="all")
prices_named = prices_named.apply(pd.to_numeric, errors="coerce")
prices_named = prices_named.ffill().bfill() # forward fill missing prices

def show_ai_section(key, title, summary):
    # Generate insight once and cache
    if key not in st.session_state.insights_cache:
        st.session_state.insights_cache[key] = chart_insight(title, summary)
    insight = st.session_state.insights_cache[key]
    st.markdown("#### AI Insight")
    st.info(insight)
    # Chat memory per chart
    if key not in st.session_state.chat_history:
        st.session_state.chat_history[key] = []
    question = st.text_input(
        f"Ask more about {title}",
        key=f"input_{key}")
    if question:
        # 🔥 FULL CONTEXT PROMPT (THIS IS THE MAGIC)
        full_prompt = f"""
You are helping a user understand stock analytics.
SECTION: {title}
DATA SUMMARY:
{summary}
INITIAL INSIGHT GIVEN:
{insight}
USER QUESTION:
{question}
Give a clear, specific answer using the data above.Dont talk about correlation with itself. Focus on what the numbers imply for the stock's performance, risk, or portfolio impact.
Avoid generic textbook explanations.
"""
        answer = ask_ai(full_prompt)
        st.session_state.chat_history[key].append(("You", question))
        st.session_state.chat_history[key].append(("AI", answer))
    # Show conversation
    for role, msg in st.session_state.chat_history[key]:
        if role == "You":
            st.markdown(f"**You:** {msg}")
        else:
            st.markdown(f"**AI:** {msg}")
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
        default=list(prices_named.columns))
    chart_df = prices_named[chart_stocks].dropna()
    # normalize ONCE properly
    normalized_df = chart_df.copy()
    for col in chart_stocks:
        normalized_df[col] = (normalized_df[col] / normalized_df[col].iloc[0]) * 100
    st.plotly_chart(
        compare_price_chart(normalized_df, chart_stocks),
        use_container_width=True)
    summary = normalized_df.tail(10).to_string()
    show_ai_section("price_chart", "Stock Price Comparison", summary)
    st.subheader("Correlation Heatmap")
    st.plotly_chart(correlation_heatmap(prices_named[chart_stocks]),
        use_container_width=True)
    corr_summary = prices_named[chart_stocks].corr().to_string()
    show_ai_section("correlation", "Stock Correlation Heatmap", corr_summary)
# ------------------ STATISTICS ------------------
with tabs[1]:
    st.subheader("Stock Statistics")
    stats_df = stock_statistics(prices_named)
    st.dataframe(stats_df, use_container_width=True)
    stats_summary = stats_df.to_string()
    show_ai_section("stats_table", "Stock Statistics Table", stats_summary)
    st.markdown("---")
    st.subheader("Bar Chart Comparison")
    metric = st.selectbox(
        "Select metric to display as bar chart",
        stats_df.columns.drop("Company"))  # exclude the company column)
    from charts import statistics_bar_chart
    st.plotly_chart(statistics_bar_chart(stats_df, metric), use_container_width=True)
    bar_summary = stats_df[[metric]].to_string()
    show_ai_section("bar_chart", f"{metric} Comparison", bar_summary)
    st.markdown("---")
    st.subheader("Daily Returns Histogram")
    from charts import daily_returns_histogram
    company_for_hist = st.selectbox(
        "Select company for daily returns histogram",
        stats_df["Company"])
    st.plotly_chart(daily_returns_histogram(prices_named, company_for_hist), use_container_width=True)
    hist_summary = prices_named[company_for_hist].describe().to_string()
    show_ai_section("histogram", "Daily Returns Histogram", hist_summary)
# ------------------ PORTFOLIO ------------------
with tabs[2]:
    st.subheader("Portfolio Construction")
    right_col, left_col = st.columns([1, 2])
    pie_placeholder = right_col.empty()
    # ---------------- SESSION STATE ----------------
    if "portfolio_weights" not in st.session_state:
        st.session_state.portfolio_weights = {}
    cols = prices_named.columns
    # initialize
    for c in cols:
        if c not in st.session_state.portfolio_weights:
            st.session_state.portfolio_weights[c] = 1 / len(cols)
    # ---------------- LEFT SIDE (SLIDERS) ----------------
    with left_col:
        st.write("Adjust weights manually (Total should be 100%)")

        weights = {}

        for c in cols:
            weights[c] = st.slider(
                c,
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.portfolio_weights.get(c, 1/len(cols)),
                step=0.01,
                key=f"slider_{c}"
            )

        # Save weights to session state
        st.session_state.portfolio_weights = weights

        # Show total so user knows if it's valid
        total_weight = sum(weights.values())
        st.write(f"**Total Weight:** {total_weight:.2%}")

    # ---------------- RIGHT SIDE (PIE CHART) ----------------
    weights_df = pd.DataFrame({
        "Company": list(weights.keys()),
        "Weight": list(weights.values())})
    fig = px.pie(weights_df, names="Company", values="Weight", hole=0.4)
    pie_placeholder.plotly_chart(fig, use_container_width=True) # only once

    # 3️⃣ Compute portfolio stats
    weight_array = np.array([
    weights[col] for col in prices_named.columns])
    portfolio_stats, portfolio_returns = compute_portfolio(
        prices_named,
        weight_array)
    # 4️⃣ Show metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Daily Return", round(portfolio_stats["Avg Daily Return"], 4))
    c2.metric("Volatility", round(portfolio_stats["Volatility"], 4))
    c3.metric("Sharpe Ratio", round(portfolio_stats["Sharpe Ratio"], 4))
    # risk score
    vol = portfolio_stats["Volatility"]
    sharpe = portfolio_stats["Sharpe Ratio"]
    vol_score = (vol - 0.005) / (0.03 - 0.005) * 100 #min-max scaling.
    sharpe_score = (3 - sharpe) / 4 * 100
    # Final risk score (weighted)
    risk_score = 0.6 * vol_score + 0.4 * sharpe_score
    risk_score = np.clip(risk_score, 0, 100)    
    st.subheader("📊 Portfolio Risk Score")
    if risk_score < 30:
        st.success(f"Low Risk 🟢 ({risk_score:.2f}/100)")
    elif risk_score < 70:
        st.warning(f"Moderate Risk 🟡 ({risk_score:.2f}/100)")
    else:
        st.error(f"High Risk 🔴 ({risk_score:.2f}/100)")
    # best vs worst contributor
    returns_df = prices_named.pct_change().fillna(0)
    weighted_returns = returns_df * weights
    contribution = weighted_returns.sum()
    contribution = contribution.sort_values(ascending=False)
    best_stock = contribution.idxmax()
    worst_stock = contribution.idxmin()
    st.subheader("📈 Best vs Worst Stock Contribution")
    st.write("🟢 Best Contributor:", best_stock)
    st.write("🔴 Worst Contributor:", worst_stock)
    # 5️⃣ Portfolio cumulative returns chart
    st.subheader("Portfolio Cumulative Returns")
    st.plotly_chart(
        portfolio_chart(portfolio_returns),
        use_container_width=True
    )
    portfolio_summary = portfolio_returns.describe().to_string()
    show_ai_section("portfolio_chart", "Portfolio Performance", portfolio_summary)
    # portfolio optimizor
    num_portfolios = 3000
    results = []
    returns = returns_df
    for _ in range(num_portfolios):
        w = np.random.random(len(prices_named.columns))
        w = w / np.sum(w)
        port_return = np.sum(returns.mean() * w)
        port_vol = np.sqrt(np.dot(w.T, np.dot(returns.cov(), w)))
        sharpe = port_return / port_vol if port_vol != 0 else 0
        results.append((sharpe, w))
    best = max(results, key=lambda x: x[0])
    best_weights = best[1]
    st.subheader("Suggested Optimal Portfolio (Sharpe Maximized)")
    col1, col2 = st.columns([1, 2],gap="large") 
    opt_df = pd.DataFrame({
        "Stock": prices_named.columns,
        "Weight": best_weights
    })
    with col1:
        st.dataframe(opt_df, width=1000, height=250)
    with col2:
        st.markdown("### 📊 Allocation Chart")
        st.bar_chart(opt_df.set_index("Stock"))
# spacing for next section
st.markdown("---")
# ============================================================
# BUILD GLOBAL DASHBOARD CONTEXT (for Smart Advisor)
# ============================================================
stats_text = stats_df.to_string()
corr_text = prices_named.corr().to_string()
portfolio_text = str(portfolio_stats)
price_summary = prices_named.describe().to_string()
def get_relevant_context(question, context):
    q = question.lower()
    if "sharpe" in q or "risk" in q or "portfolio" in q:
        return context.split("CORRELATIONS:")[0] + "\n" + context.split("PORTFOLIO METRICS:")[1]
    if "correlation" in q:
        return context.split("CORRELATIONS:")[1].split("PORTFOLIO METRICS:")[0]
    if "price" in q or "return" in q:
        return context.split("PRICE SUMMARY:")[1]
    if "stock" in q:
        return context.split("STOCK STATISTICS:")[1].split("CORRELATIONS:")[0]
    return context
dashboard_context = f"""
STOCK STATISTICS:
{stats_text}
CORRELATIONS:
{corr_text}
PORTFOLIO METRICS:
{portfolio_text}
PRICE SUMMARY:
{price_summary}
"""
# ============================================================
# FLOATING SMART ADVISOR UI
# ============================================================
from ai_utils import ask_dashboard_question
# Memory
if "advisor_open" not in st.session_state:
    st.session_state.advisor_open = False
if "advisor_history" not in st.session_state:
    st.session_state.advisor_history = []
# Floating button CSS
st.markdown("""
<style>
.advisor-btn {
    position: fixed;
    bottom: 20px;
    right: 40px;
    z-index: 1000;
}

</style>
""", unsafe_allow_html=True)

# Floating toggle button
st.markdown('<div class="advisor-btn">', unsafe_allow_html=True)
if st.button("Chat"):
    st.session_state.advisor_open = not st.session_state.advisor_open
st.markdown('</div>', unsafe_allow_html=True)
# Chat window
if st.session_state.advisor_open:
    st.markdown('<div class="advisor-box">', unsafe_allow_html=True)
    st.markdown("### Smart Advisor")
    # Show chat history
    for role, msg in st.session_state.advisor_history:
        if role == "You":
            st.write("YOU : ", msg)
        else:
            st.write("ADVISOR : ", msg)
    with st.form("advisor_form", clear_on_submit=True):
        user_q = st.text_input("Ask about portfolio, risk, market outlook")
        send = st.form_submit_button("Send")
    if send and user_q:
        history_text = "\n".join([f"{r}: {m}" for r, m in st.session_state.advisor_history])
        answer = ask_dashboard_question(
            user_q,
            dashboard_context,
            history_text)
        st.session_state.advisor_history.append(("You", user_q))
        st.session_state.advisor_history.append(("AI", answer))
        st.session_state.advisor_input = ""  # 🔥 clears input
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)