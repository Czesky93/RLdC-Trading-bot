"""Relative Strength Index (RSI) indicator."""

from __future__ import annotations

import pandas as pd


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Compute RSI for a price series."""

    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(0)
