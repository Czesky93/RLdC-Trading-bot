import pandas as pd
import ta
import os

def backtest_strategy(symbol="BTCUSDT", initial_balance=1000, trade_risk=0.02):
    """Testowanie strategii na danych historycznych"""
    file_name = f"market_data_{symbol}.csv"

    if not os.path.exists(file_name):
        print(f"🚨 Brak danych rynkowych dla {symbol}!")
        return

    df = pd.read_csv(file_name)
    if df.empty or "close" not in df:
        print(f"🚨 Plik {file_name} jest pusty lub uszkodzony!")
        return

    df["EMA_9"] = ta.trend.EMAIndicator(df["close"], window=9).ema_indicator()
    df["EMA_21"] = ta.trend.EMAIndicator(df["close"], window=21).ema_indicator()
    df["MACD"] = ta.trend.MACD(df["close"]).macd()
    df["RSI"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    df["ADX"] = ta.trend.ADXIndicator(df["high"], df["low"], df["close"]).adx()
    bb = ta.volatility.BollingerBands(df["close"])
    df["BB_Upper"], df["BB_Lower"] = bb.bollinger_hband(), bb.bollinger_lband()

    balance = initial_balance
    position = 0
    trade_log = []

    for i in range(1, len(df)):
        price = df["close"].iloc[i]
        ema_9, ema_21 = df["EMA_9"].iloc[i], df["EMA_21"].iloc[i]
        macd, rsi, adx = df["MACD"].iloc[i], df["RSI"].iloc[i], df["ADX"].iloc[i]
        bb_upper, bb_lower = df["BB_Upper"].iloc[i], df["BB_Lower"].iloc[i]

        if position == 0 and ema_9 > ema_21 and macd > 0 and rsi < 70 and adx > 25 and price < bb_lower:
            position = (trade_risk * balance) / price  # Obliczenie pozycji
            balance -= position * price
            trade_log.append((df["timestamp"].iloc[i], "BUY", price, balance))

        elif position > 0 and (ema_9 < ema_21 or macd < 0 or rsi > 70 or price > bb_upper):
            balance += position * price
            trade_log.append((df["timestamp"].iloc[i], "SELL", price, balance))
            position = 0

    # Podsumowanie backtestingu
    final_balance = balance + (position * df["close"].iloc[-1])
    print(f"📈 Strategia dla {symbol} zakończona! Start: {initial_balance} USDT, Koniec: {final_balance:.2f} USDT")
    return trade_log

# Testowanie strategii na danych historycznych
symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
for symbol in symbols:
    backtest_strategy(symbol)
