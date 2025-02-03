import pandas as pd
import ta
import random

def optimize_strategy(symbol="BTCUSDT", data_file="market_data_BTCUSDT.csv", iterations=50):
    """AI AutoML – optymalizacja strategii tradingowej"""
    
    df = pd.read_csv(data_file)
    if df.empty or "close" not in df:
        print(f"🚨 Brak poprawnych danych dla {symbol}!")
        return

    best_config = None
    best_profit = -float("inf")

    for _ in range(iterations):
        # Losowanie parametrów strategii
        ema_short = random.randint(5, 15)
        ema_long = random.randint(20, 50)
        macd_short = random.randint(10, 20)
        macd_long = random.randint(26, 40)
        rsi_period = random.randint(10, 20)

        # Obliczenie wskaźników technicznych
        df["EMA_Short"] = ta.trend.EMAIndicator(df["close"], window=ema_short).ema_indicator()
        df["EMA_Long"] = ta.trend.EMAIndicator(df["close"], window=ema_long).ema_indicator()
        df["MACD"] = ta.trend.MACD(df["close"], window_slow=macd_long, window_fast=macd_short).macd()
        df["RSI"] = ta.momentum.RSIIndicator(df["close"], window=rsi_period).rsi()

        balance = 1000
        position = 0

        for i in range(1, len(df)):
            price = df["close"].iloc[i]
            if position == 0 and df["EMA_Short"].iloc[i] > df["EMA_Long"].iloc[i] and df["MACD"].iloc[i] > 0 and df["RSI"].iloc[i] < 70:
                position = balance / price
                balance -= position * price
            elif position > 0 and df["EMA_Short"].iloc[i] < df["EMA_Long"].iloc[i] and df["MACD"].iloc[i] < 0 and df["RSI"].iloc[i] > 30:
                balance += position * price
                position = 0

        final_profit = balance + (position * df["close"].iloc[-1] if position > 0 else 0)

        if final_profit > best_profit:
            best_profit = final_profit
            best_config = (ema_short, ema_long, macd_short, macd_long, rsi_period)

    print(f"🏆 Najlepsza konfiguracja dla {symbol}: EMA ({best_config[0]}/{best_config[1]}), MACD ({best_config[2]}/{best_config[3]}), RSI ({best_config[4]})")
    print(f"📈 Zysk: {best_profit:.2f} USDT")
    return best_config

# Testowanie optymalizacji na danych BTCUSDT
optimize_strategy("BTCUSDT")
