SECTOR_MAP = {
    "Technology": {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Google": "GOOGL",
        "Amazon": "AMZN",
        "Meta": "META",
        "NVIDIA": "NVDA"
    },
    "Automobile": {
        "Tesla": "TSLA",
        "Ford": "F",
        "BMW": "BMW.DE",
        "Toyota": "TM"
    },
    "Finance": {
        "JPMorgan": "JPM",
        "Goldman Sachs": "GS",
        "Morgan Stanley": "MS",
        "HDFC Bank": "HDFCBANK.NS"
    },
    "Energy": {
        "ExxonMobil": "XOM",
        "Chevron": "CVX",
        "Reliance": "RELIANCE.NS"
    },
    "Healthcare": {
        "Pfizer": "PFE",
        "Johnson & Johnson": "JNJ",
        "Moderna": "MRNA"
    }
}

TICKER_TO_COMPANY = {
    v: k
    for sector in SECTOR_MAP.values()
    for k, v in sector.items()
}
