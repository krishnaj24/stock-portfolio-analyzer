# Stock Portfolio Analyzer

This project is a **Stock Portfolio Analyzer web application** developed using **Python and Streamlit**.

The application allows users to:
- Search for stocks using company name or ticker
- Add selected stocks to a portfolio
- Analyze daily stock returns
- Visualize return distribution and volatility
- Calculate and display cumulative portfolio returns

Real-time stock price data is fetched using the **Yahoo Finance API**.

---

## Technologies Used
- Python
- Streamlit
- Pandas, NumPy
- Plotly
- yfinance

---

## How to Run the Project

### Step 1: Clone the repository
git clone <github-repo-link>
cd <project-folder>

### Step 2: (Optional) Create virtual environment
python -m venv venv

venv\Scripts\activate

### Step 3: Install dependencies
pip install -r requirements.txt

### Step 4: Run the application
streamlit run app.py
