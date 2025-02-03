import json
import os
import openai

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    print("🚨 Brak pliku config.json! Ustaw domyślną konfigurację.")
    exit(1)

with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)

OPENAI_API_KEY = config["OPENAI_API_KEY"]
USE_FREE_AI = config["USE_FREE_AI"]
USE_PAID_AI = config["USE_PAID_AI"]
openai.api_key = OPENAI_API_KEY

def analyze_trade_results(trade_history):
    """AI analizuje historię transakcji i optymalizuje strategię"""
    trade_data = json.dumps(trade_history)

    prompt = f"""
    Oto historia transakcji:

    {trade_data}

    - Jakie błędy popełniła strategia?
    - Jakie poprawki należy wprowadzić, aby zmaksymalizować zyski i zminimalizować straty?
    - Jakie ustawienia powinny zostać zoptymalizowane?

    Odpowiedź:
    """

    model_choice = "gpt-4-turbo" if USE_PAID_AI else "gpt-3.5-turbo" if not USE_FREE_AI else "gpt4all"

    response = openai.ChatCompletion.create(
        model=model_choice,
        messages=[{"role": "system", "content": "Jesteś ekspertem optymalizacji strategii tradingowych."},
                  {"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]

if __name__ == "__main__":
    sample_trade_history = [{"pair": "BTCUSDT", "profit": -50, "strategy": "EMA"}, {"pair": "ETHUSDT", "profit": 120, "strategy": "AI"}]
    optimization_report = analyze_trade_results(sample_trade_history)
    print(f"📊 AI Optymalizacja Strategii:
{optimization_report}")
