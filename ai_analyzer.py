import gpt4all
import pandas as pd

model = gpt4all.GPT4All("gpt4all-model.bin")

def analyze_market():
    df = pd.read_csv("market_data.csv")
    last_price = df["close"].iloc[-1]

    prompt = f"Cena ostatniej świecy to {last_price} USDT. Czy powinienem KUPIĆ, SPRZEDAĆ, czy TRZYMAĆ?"
    response = model.generate(prompt)
    return response.strip().upper()

print(f"📈 AI rekomenduje: {analyze_market()}")
