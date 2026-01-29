import pandas as pd

from rldc.signals.engine import evaluate_signal


def test_evaluate_signal():
    df = pd.DataFrame(
        {
            "timestamp": [1, 2, 3, 4],
            "open": [1, 1, 1, 1],
            "high": [1, 1, 1, 1],
            "low": [1, 1, 1, 1],
            "close": [1, 1.1, 1.2, 1.1],
            "volume": [10, 10, 10, 10],
        }
    )
    result = evaluate_signal(df)
    assert "signal" in result
    assert "levels" in result
