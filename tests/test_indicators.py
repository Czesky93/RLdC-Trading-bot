import pandas as pd

from rldc.indicators.bollinger import compute_bollinger
from rldc.indicators.macd import compute_macd
from rldc.indicators.rsi import compute_rsi


def test_indicators_shape():
    series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    rsi = compute_rsi(series)
    macd = compute_macd(series)
    bollinger = compute_bollinger(series, window=3)

    assert len(rsi) == len(series)
    assert set(macd.columns) == {"macd", "signal", "hist"}
    assert set(bollinger.columns) == {"middle", "upper", "lower"}
