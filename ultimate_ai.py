import json
import os
import openai
import numpy as np
import requests
import pandas as pd
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
        "TAKE_PROFIT": 0.05,
        "ENABLE_QUANTUM_AI": True,
        "ENABLE_HFT": True,
        "ENABLE_BLOCKCHAIN_ANALYSIS": True
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(default_config, f, indent=4)

with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)

OPENAI_API_KEY = config["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

def analyze_future_market():
    """AI przewiduje przyszłość rynków na podstawie globalnych danych"""
    market_data = requests.get("https://api.coingecko.com/api/v3/global").json()
    
    prompt = f"""
    Oto aktualne dane rynkowe:

    {market_data}

    - Jakie są możliwe scenariusze dla rynku kryptowalut i finansowego w ciągu najbliższych 24 godzin?
    - Jakie strategie będą najbardziej skuteczne?
    - Jakie wydarzenia geopolityczne mogą wpłynąć na rynek?

    Odpowiedź:
    """

    model_choice = "gpt-4-turbo" if config["USE_PAID_AI"] else "gpt-3.5-turbo" if not config["USE_FREE_AI"] else "gpt4all"

    response = openai.ChatCompletion.create(
        model=model_choice,
        messages=[{"role": "system", "content": "Jesteś sztuczną inteligencją przewidującą rynki finansowe."},
                  {"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]

@app.route("/")
def index():
    """Główna strona ULTIMATE AI"""
    return render_template("ultimate_ai.html")

@app.route("/predict", methods=["GET"])
def predict():
    """API przewidujące przyszłość rynków"""
    prediction = analyze_future_market()
    return jsonify({"prediction": prediction})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, debug=True)
