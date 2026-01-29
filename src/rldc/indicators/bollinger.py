"""Bollinger Bands indicator."""

from __future__ import annotations

import pandas as pd


def compute_bollinger(series: pd.Series, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    """Compute Bollinger Bands."""

    sma = series.rolling(window=window, min_periods=window).mean()
    std = series.rolling(window=window, min_periods=window).std()
    upper = sma + num_std * std
    lower = sma - num_std * std
    return pd.DataFrame({"middle": sma, "upper": upper, "lower": lower})
