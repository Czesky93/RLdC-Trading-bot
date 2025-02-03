import pandas as pd
from ta.trend import EMAIndicator

def get_trading_signal():
    df = pd.read_csv("market_data.csv")
    df["EMA_9"] = EMAIndicator(df["close"], window=9).ema_indicator()
    df["EMA_21"] = EMAIndicator(df["close"], window=21).ema_indicator()

    if df["EMA_9"].iloc[-1] > df["EMA_21"].iloc[-1]:
        return "KUP"
    elif df["EMA_9"].iloc[-1] < df["EMA_21"].iloc[-1]:
        return "SPRZEDAJ"
    else:
        return "TRZYMAJ"

print(f"💰 Strategia EMA: {get_trading_signal()}")
