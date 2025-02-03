import os
import pandas as pd
import ta

LOG_FILE = "strategy_log.txt"

def log_decision(symbol, decision):
    """Zapisuje decyzję do pliku logów"""
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{symbol}: {decision}\n")

def get_advanced_trading_signal(symbol="BTCUSDT"):
    """Zaawansowana analiza rynku i generowanie sygnału kupna/sprzedaży"""
    file_name = f"market_data_{symbol}.csv"

    if not os.path.exists(file_name):
        print(f"🚨 Brak danych rynkowych dla {symbol}!")
        return "BRAK DANYCH"

    df = pd.read_csv(file_name)

    if df.empty or "close" not in df:
        print(f"🚨 Plik {file_name} jest pusty lub uszkodzony!")
        return "BŁĄD DANYCH"

    # Obliczenie wskaźników technicznych
    df["EMA_9"] = ta.trend.EMAIndicator(df["close"], window=9).ema_indicator()
    df["EMA_21"] = ta.trend.EMAIndicator(df["close"], window=21).ema_indicator()
    df["MACD"] = ta.trend.MACD(df["close"]).macd()
    df["RSI"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    df["ADX"] = ta.trend.ADXIndicator(df["high"], df["low"], df["close"]).adx()
    bb = ta.volatility.BollingerBands(df["close"])
    df["BB_Upper"], df["BB_Lower"] = bb.bollinger_hband(), bb.bollinger_lband()

    ema_9, ema_21 = df["EMA_9"].iloc[-1], df["EMA_21"].iloc[-1]
    macd, rsi, adx = df["MACD"].iloc[-1], df["RSI"].iloc[-1], df["ADX"].iloc[-1]
    bb_upper, bb_lower = df["BB_Upper"].iloc[-1], df["BB_Lower"].iloc[-1]

    # Strategia na podstawie EMA, MACD, RSI, ADX, Bollinger Bands
    if ema_9 > ema_21 and macd > 0 and rsi < 70 and adx > 25 and df["close"].iloc[-1] < bb_lower:
        decision = "KUP"
    elif ema_9 < ema_21 and macd < 0 and rsi > 30 and adx > 25 and df["close"].iloc[-1] > bb_upper:
        decision = "SPRZEDAJ"
    else:
        decision = "TRZYMAJ"

    log_decision(symbol, decision)
    return decision

# Test dla różnych par walutowych
symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
for symbol in symbols:
    decision = get_advanced_trading_signal(symbol)
    print(f"📊 Zaawansowana strategia dla {symbol}: {decision}")
