# stock-portfolio-analyzer
An interactive dashboard to analyze stocks, build portfolios, simulate investment performance, and get AI-powered insights.
Features:
1. Multi-market stock selection
2. Stock statistics & comparison charts
3. Correlation heatmap
4. Portfolio builder with weight sliders
5. Investment growth simulation
6. Portfolio risk score calculation
7. AI chart insights & Smart Advisor chat

Tech Stack:
Python
Streamlit
Plotly
Pandas & NumPy
Yahoo Finance API (yfinance)
OpenRouter API (for AI insights)

Run the Project Locally:
1. Clone Repository
git clone https://github.com/krishnaj24/stock-portfolio-analyzer
cd stock-portfolio-analyzer

2. Install Dependencies
pip install -r requirements.txt

3. Setup AI Features (Optional)
This project uses OpenRouter API for AI-generated insights.
Create a file named .env in the project root and add:
OPENROUTER_API_KEY=your_api_key_here

4. Run the App
streamlit run app.py
