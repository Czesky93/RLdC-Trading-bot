import pandas as pd
import ta
import os

def detect_pump_and_dump(symbol="BTCUSDT", threshold=5, data_file="market_data_BTCUSDT.csv"):
    """Wykrywanie nagłych wzrostów/spadków cen (Pump & Dump)"""
    
    if not os.path.exists(data_file):
        print(f"🚨 Brak danych rynkowych dla {symbol}!")
        return

    df = pd.read_csv(data_file)
    if df.empty or "close" not in df:
        print(f"🚨 Plik {data_file} jest pusty lub uszkodzony!")
        return

    df["returns"] = df["close"].pct_change() * 100  # Obliczenie procentowej zmiany ceny

    alerts = []
    for i in range(1, len(df)):
        if df["returns"].iloc[i] > threshold:
            alerts.append((df["timestamp"].iloc[i], "🚀 Możliwy Pump!", df["returns"].iloc[i]))
        elif df["returns"].iloc[i] < -threshold:
            alerts.append((df["timestamp"].iloc[i], "⚠️ Możliwy Dump!", df["returns"].iloc[i]))

    if alerts:
        print(f"📢 Wykryto {len(alerts)} podejrzane ruchy na rynku dla {symbol}:")
        for alert in alerts:
            print(f"{alert[0]} - {alert[1]} | Zmiana: {alert[2]:.2f}%")
    else:
        print(f"✅ Brak oznak manipulacji rynku dla {symbol}")

    return alerts

# Testowanie wykrywania Pump & Dump
symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
for symbol in symbols:
    detect_pump_and_dump(symbol)
