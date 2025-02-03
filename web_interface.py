import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    print("🚨 Brak pliku config.json! Tworzenie domyślnej konfiguracji...")
    default_config = {
        "AI_MODE": "hybrid",
        "USE_FREE_AI": True,
        "USE_PAID_AI": True,
        "START_BALANCE": 1000,
        "STOP_LOSS": 0.02,
        "TAKE_PROFIT": 0.05
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(default_config, f, indent=4)

with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)

app = Flask(__name__)

@app.route("/")
def index():
    """Główna strona panelu WWW"""
    return render_template("dashboard.html", config=config)

@app.route("/update_config", methods=["POST"])
def update_config():
    """Aktualizacja ustawień AI i strategii"""
    data = request.get_json()
    config.update(data)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    return jsonify({"message": "✅ Konfiguracja zaktualizowana!"})

@app.route("/get_logs")
def get_logs():
    """Pobieranie logów transakcji"""
    log_file = "logs/trades_log.txt"
    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            logs = file.readlines()
        return jsonify({"logs": logs})
    return jsonify({"error": "Brak logów!"})

@app.route("/plot_trading_chart")
def plot_trading_chart():
    """Generowanie wykresu wyników handlowych"""
    data_file = "market_data_BTCUSDT.csv"
    if not os.path.exists(data_file):
        return jsonify({"error": "Brak danych rynkowych!"})

    df = pd.read_csv(data_file)
    plt.figure(figsize=(10, 5))
    plt.plot(df["timestamp"], df["close"], label="Cena BTC")
    plt.xlabel("Czas")
    plt.ylabel("Cena (USDT)")
    plt.legend()
    plt.savefig("static/trading_chart.png")
    return jsonify({"message": "✅ Wykres zaktualizowany!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
