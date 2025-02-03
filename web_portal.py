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
        "USE_PAID_AI": False,
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
    """Główna strona zaawansowanego portalu"""
    return render_template("futuristic_dashboard.html", config=config)

@app.route("/update_config", methods=["POST"])
def update_config():
    """Aktualizacja ustawień bota"""
    data = request.get_json()
    config.update(data)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    return jsonify({"message": "✅ Konfiguracja zaktualizowana!"})

@app.route("/get_trading_chart")
def get_trading_chart():
    """Generowanie wykresu strategii handlowych"""
    data_file = "market_data_BTCUSDT.csv"
    if not os.path.exists(data_file):
        return jsonify({"error": "Brak danych rynkowych!"})

    df = pd.read_csv(data_file)
    plt.figure(figsize=(12, 6))
    plt.plot(df["timestamp"], df["close"], label="Cena BTC", color="cyan")
    plt.xlabel("Czas")
    plt.ylabel("Cena (USDT)")
    plt.grid(True, linestyle="--", color="gray")
    plt.legend()
    plt.savefig("static/futuristic_trading_chart.png")
    return jsonify({"message": "✅ Wykres zaktualizowany!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
