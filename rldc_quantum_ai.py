import numpy as np
import pandas as pd
import ta
import openai
import json
import os
from scipy.optimize import minimize

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    print("🚨 Brak pliku config.json! Ustaw API OpenAI.")
    exit(1)

with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)

OPENAI_API_KEY = config["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

def quantum_optimization(price_data):
    """Wykorzystuje optymalizację kwantową do predykcji trendów rynkowych"""
    
    def loss_function(params):
        ema_short, ema_long, rsi_period = params
        df = price_data.copy()
        df["EMA_Short"] = ta.trend.EMAIndicator(df["close"], window=int(ema_short)).ema_indicator()
        df["EMA_Long"] = ta.trend.EMAIndicator(df["close"], window=int(ema_long)).ema_indicator()
        df["RSI"] = ta.momentum.RSIIndicator(df["close"], window=int(rsi_period)).rsi()

        signals = ((df["EMA_Short"] > df["EMA_Long"]) & (df["RSI"] < 70)).astype(int)
        returns = df["close"].pct_change() * signals.shift(1)
        return -returns.sum()  # Minimalizujemy stratę, maksymalizujemy zysk

    result = minimize(loss_function, [9, 21, 14], bounds=[(5, 15), (20, 50), (10, 30)])
    return {"EMA_Short": result.x[0], "EMA_Long": result.x[1], "RSI_Period": result.x[2]}

def analyze_market_with_ai(market_data):
    """AI GPT-4 Turbo analizuje sytuację rynkową"""
    prompt = f"""
    Oto dane rynkowe:

    {market_data}

    - Jakie są możliwe scenariusze dla rynku kryptowalut w ciągu najbliższych 24 godzin?
    - Jakie strategie są najbardziej optymalne?
    - Czy istnieją sygnały silnej manipulacji lub interwencji?

    Odpowiedź:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "Jesteś ekspertem analizy finansowej i tradingu kwantowego."},
                  {"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]

if __name__ == "__main__":
    print("🚀 RLdC Quantum AI aktywowane!")
    df = pd.DataFrame({"close": np.random.rand(100) * 50000})  # Symulacja danych cenowych BTC
    best_params = quantum_optimization(df)
    print(f"📊 Najlepsze parametry strategii kwantowej: {best_params}")

    market_analysis = analyze_market_with_ai("BTC: $42,500, ETH: $3,200, S&P500: 4,150")
    print(f"🧠 AI Market Analysis:
{market_analysis}")
