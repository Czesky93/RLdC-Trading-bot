import requests
import json

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    print("🚨 Brak pliku config.json! Ustaw dostęp do API.")
    exit(1)

with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)

BINANCE_API_URL = "https://api.binance.com/api/v3/depth"

def track_whale_activity(symbol="BTCUSDT", threshold=500):
    """Śledzenie wielkich transakcji (Whale Tracking)"""
    
    params = {"symbol": symbol, "limit": 500}
    response = requests.get(BINANCE_API_URL, params=params)
    order_book = response.json()

    large_bids = [float(order[1]) for order in order_book["bids"] if float(order[1]) > threshold]
    large_asks = [float(order[1]) for order in order_book["asks"] if float(order[1]) > threshold]

    if large_bids:
        print(f"🐳 Wykryto duże ZAKUPY dla {symbol}: {large_bids}")
    if large_asks:
        print(f"🐋 Wykryto duże SPRZEDAŻE dla {symbol}: {large_asks}")

    return large_bids, large_asks

# Testowanie Whale Tracking na BTCUSDT
track_whale_activity("BTCUSDT")
