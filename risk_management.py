import pandas as pd
import ta
import os

def risk_management(symbol="BTCUSDT", initial_balance=1000, risk_per_trade=0.02, take_profit_factor=2):
    """Strategia z dynamicznym stop-loss i take-profit"""
    file_name = f"market_data_{symbol}.csv"

    if not os.path.exists(file_name):
        print(f"🚨 Brak danych rynkowych dla {symbol}!")
        return

    df = pd.read_csv(file_name)
    if df.empty or "close" not in df:
        print(f"🚨 Plik {file_name} jest pusty lub uszkodzony!")
        return

    df["ATR"] = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"]).average_true_range()

    balance = initial_balance
    position = 0
    trade_log = []

    for i in range(1, len(df)):
        price = df["close"].iloc[i]
        atr = df["ATR"].iloc[i]
        stop_loss = price - (atr * 1.5)  # Stop-loss na 1.5x ATR
        take_profit = price + (atr * take_profit_factor)  # Take-profit na 2x ATR

        if position == 0 and df["close"].iloc[i] > df["close"].iloc[i - 1]:  # Warunek wejścia (można dodać strategię)
            position = (risk_per_trade * balance) / price  # Obliczenie pozycji
            balance -= position * price
            trade_log.append((df["timestamp"].iloc[i], "BUY", price, stop_loss, take_profit, balance))

        elif position > 0 and (price <= stop_loss or price >= take_profit):  # Warunek wyjścia
            balance += position * price
            trade_log.append((df["timestamp"].iloc[i], "SELL", price, balance))
            position = 0

    final_balance = balance + (position * df["close"].iloc[-1] if position > 0 else 0)
    print(f"📊 Strategia ryzyka dla {symbol} zakończona! Start: {initial_balance} USDT, Koniec: {final_balance:.2f} USDT")
    return trade_log

# Testowanie strategii zarządzania ryzykiem
symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
for symbol in symbols:
    risk_management(symbol)
