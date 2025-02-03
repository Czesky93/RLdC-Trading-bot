import os
import json
from binance.client import Client
from trading_strategy_advanced import get_advanced_trading_signal

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    print("🚨 Brak pliku config.json! Ustaw swoje klucze API.")
    exit(1)

with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)

API_KEY = config["BINANCE_API_KEY"]
API_SECRET = config["BINANCE_API_SECRET"]

client = Client(API_KEY, API_SECRET)

def place_order(symbol="BTCUSDT", amount=0.001):
    """Automatyczne składanie zleceń na Binance"""
    signal = get_advanced_trading_signal(symbol)
    
    if signal == "KUP":
        order = client.order_market_buy(symbol=symbol, quantity=amount)
        print(f"✅ Złożono zlecenie KUP {amount} {symbol}: {order}")
    elif signal == "SPRZEDAJ":
        order = client.order_market_sell(symbol=symbol, quantity=amount)
        print(f"✅ Złożono zlecenie SPRZEDAŻ {amount} {symbol}: {order}")
    else:
        print(f"📊 Brak akcji dla {symbol}, strategia: {signal}")

# Automatyczne składanie zleceń co 5 minut
import time
while True:
    symbols = ["BTCUSDT", "ETHUSDT"]
    for symbol in symbols:
        place_order(symbol, amount=0.001)  # Standardowy wolumen transakcji
    time.sleep(300)
