import requests

BINANCE_API_URL = "https://api.binance.com/api/v3/klines"

def get_market_data(symbol, interval="1h"):
    params = {"symbol": symbol, "interval": interval, "limit": 100}
    response = requests.get(BINANCE_API_URL, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching market data: {response.status_code}")
        return None
