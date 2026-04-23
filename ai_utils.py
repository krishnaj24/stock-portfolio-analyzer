import requests
import os
import streamlit as st
def ask_ai(prompt):

    api_key = st.secrets["OPENROUTER_API_KEY"]

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://stock-portfolio-analyzer.streamlit.app",
        "X-Title": "Stock Portfolio Analyzer",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful financial assistant. Explain stock charts, portfolio stats and market concepts in simple language."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if "error" in result:
        return f"API Error: {result['error']}"

    return result["choices"][0]["message"]["content"]
def chart_insight(chart_title, data_summary):
    prompt = f"""
You are a stock market analyst.

Give ONLY 2–3 short bullet insights from the data.
Use:
🟢 for positive signals
🔴 for risk signals
Rules:
- Keep the red and green dots at the start of the line which shows insights.
- each insight should be on new line
- after mentioning a positive or negative signal, go to the next line to mention other signals or points
- DO NOT say "Here are insights"
- DO NOT USE RANDOM EMOJIS, only use the ones mentioned above
- Speak like you are directly talking to the user
- Focus on what the numbers *imply*
- Speak if the stock is worth buying, holding or selling based on the data
- after mentioning the insights, give a one line summary of the overall chart in simple language
Chart: {chart_title}

Data Summary:
{data_summary}
"""
    return ask_ai(prompt)
# ================= SMART ADVISOR (RAG) =================

def ask_dashboard_question(user_question, dashboard_context, chat_history):
    prompt = f"""
You are a professional financial advisor helping a user understand their stock dashboard.

You have 3 knowledge sources:
1) Dashboard data below (MOST IMPORTANT)
2) Financial knowledge
3) Market reasoning

DASHBOARD DATA:
{dashboard_context}

CONVERSATION HISTORY:
{chat_history}

USER QUESTION:
{user_question}

Rules:
- If question is about THEIR stocks → use dashboard data heavily
- If question is about future → give reasoning, NOT prediction
- If question is general finance → explain simply
- Be specific and practical, not textbook.
- Give small 2 line answers which includes the reason behind it.

Answer:
"""

    return ask_ai(prompt)