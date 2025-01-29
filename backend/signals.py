import talib
import numpy as np

def generate_signal(prices):
    rsi = talib.RSI(np.array(prices), timeperiod=14)
    if rsi[-1] < 30:
        return "BUY"
    elif rsi[-1] > 70:
        return "SELL"
    return "HOLD"
