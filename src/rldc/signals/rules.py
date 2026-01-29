"""Signal rules for RLdC Trading AiNalyzer Bot."""

from __future__ import annotations

import pandas as pd


def generate_signal(indicators: dict[str, float]) -> tuple[str, str]:
    """Generate BUY/SELL/WAIT signal based on indicators.

    Returns a tuple: (signal, rationale).
    """

    rsi = indicators.get("rsi", 0)
    macd = indicators.get("macd", 0)
    macd_signal = indicators.get("macd_signal", 0)

    if rsi <= 30 and macd > macd_signal:
        return "BUY", "RSI poniżej 30 i MACD powyżej linii sygnału (ostrożnie)."
    if rsi >= 70 and macd < macd_signal:
        return "SELL", "RSI powyżej 70 i MACD poniżej linii sygnału (ostrożnie)."
    return "WAIT", "Brak jednoznacznego sygnału w prostych regułach."


def summarize_indicators(df: pd.DataFrame) -> dict[str, float]:
    """Extract latest indicator values from dataframe."""

    latest = df.iloc[-1]
    return {
        "rsi": float(latest.get("rsi", 0)),
        "macd": float(latest.get("macd", 0)),
        "macd_signal": float(latest.get("macd_signal", 0)),
        "bb_upper": float(latest.get("bb_upper", 0)),
        "bb_lower": float(latest.get("bb_lower", 0)),
        "tenkan": float(latest.get("tenkan", 0)),
        "kijun": float(latest.get("kijun", 0)),
    }
