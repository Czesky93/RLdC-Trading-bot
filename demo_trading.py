import pandas as pd
import ta
import numpy as np
import random
import json
import os
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify

CONFIG_FILE = "config.json"
if not os.path.exists(CONFIG_FILE):
    print("🚨 Brak pliku config.json! Tworzenie domyślnej konfiguracji...")
    default_config = {
        "AI_MODE": "hybrid",
        "USE_FREE_AI": True,
        "USE_PAID_AI": True,
        "START_BALANCE": 1000
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(default_config, f, indent=4)

with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)

app = Flask(__name__)

def simulate_trade(strategy_name, start_balance=1000, trade_risk=0.02, data_file="market_data_BTCUSDT.csv"):
    """Symulacja strategii tradingowej"""
    
    if not os.path.exists(data_file):
        return {"error": "Brak danych rynkowych!"}

    df = pd.read_csv(data_file)
    df["EMA_9"] = ta.trend.EMAIndicator(df["close"], window=9).ema_indicator()
    df["EMA_21"] = ta.trend.EMAIndicator(df["close"], window=21).ema_indicator()
    df["RSI"] = ta.momentum.RSIIndicator(df["close"]).rsi()

    balance = start_balance
    position = 0
    history = []

    for i in range(1, len(df)):
        price = df["close"].iloc[i]
        rsi = df["RSI"].iloc[i]

        if position == 0 and rsi < 30:  # Kupno przy wyprzedaniu rynku
            position = (trade_risk * balance) / price
            balance -= position * price
            history.append((df["timestamp"].iloc[i], "BUY", price, balance))
        elif position > 0 and rsi > 70:  # Sprzedaż przy wykupieniu rynku
            balance += position * price
            history.append((df["timestamp"].iloc[i], "SELL", price, balance))
            position = 0

    final_balance = balance + (position * df["close"].iloc[-1] if position > 0 else 0)
    return {"strategy": strategy_name, "final_balance": final_balance, "history": history}

@app.route("/simulate", methods=["POST"])
def simulate():
    """API do uruchomienia symulacji"""
    data = request.get_json()
    strategies = data.get("strategies", [])
    start_balance = data.get("start_balance", 1000)

    results = [simulate_trade(strategy, start_balance) for strategy in strategies]
    return jsonify(results)

@app.route("/")
def index():
    """Główna strona interfejsu"""
    return render_template("demo_trading.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
