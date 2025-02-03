import openai
import json
import os

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    print("🚨 Brak pliku config.json! Ustaw API OpenAI.")
    exit(1)

with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)

OPENAI_API_KEY = config["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

def analyze_market_with_gpt(market_data):
    """Analiza rynku przy użyciu GPT-4 Turbo"""
    prompt = f"""
    Oto najnowsze dane rynkowe:

    {market_data}

    Jakie są możliwe scenariusze dla rynku kryptowalut w ciągu najbliższych 24 godzin?
    Jakie strategie tradingowe są optymalne na podstawie tych danych?
    """

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "Jesteś ekspertem analizy finansowej i predykcji rynków."},
                  {"role": "user", "content": prompt}]
    )

    analysis = response["choices"][0]["message"]["content"]
    print(f"📊 GPT-4 Turbo Analiza Rynkowa:
{analysis}")
    return analysis

# Przykładowe testowanie
if __name__ == "__main__":
    test_data = "Bitcoin: $42,500, Ethereum: $3,200, S&P500: 4,150, Zmiana: -2.3%"
    analyze_market_with_gpt(test_data)
