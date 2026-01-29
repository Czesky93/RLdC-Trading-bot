"""Signal engine that computes indicators and signals."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import pandas as pd

from rldc.indicators.bollinger import compute_bollinger
from rldc.indicators.ichimoku import compute_ichimoku
from rldc.indicators.macd import compute_macd
from rldc.indicators.rsi import compute_rsi
from rldc.signals.risk import compute_levels
from rldc.signals.rules import generate_signal, summarize_indicators

logger = logging.getLogger(__name__)


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Attach indicators to OHLCV dataframe."""

    df = df.copy()
    df["rsi"] = compute_rsi(df["close"])
    macd = compute_macd(df["close"])
    df["macd"] = macd["macd"]
    df["macd_signal"] = macd["signal"]

    bollinger = compute_bollinger(df["close"])
    df["bb_upper"] = bollinger["upper"]
    df["bb_lower"] = bollinger["lower"]

    ichimoku = compute_ichimoku(df)
    df["tenkan"] = ichimoku["tenkan"]
    df["kijun"] = ichimoku["kijun"]

    return df


def evaluate_signal(df: pd.DataFrame) -> dict:
    """Evaluate the latest signal and risk levels."""

    if df.empty:
        raise ValueError("Brak danych do analizy.")

    enriched = compute_indicators(df)
    indicators = summarize_indicators(enriched)
    signal, rationale = generate_signal(indicators)
    latest_close = float(enriched.iloc[-1]["close"])
    levels = compute_levels(latest_close, signal)

    return {
        "timestamp": int(datetime.now(tz=timezone.utc).timestamp()),
        "signal": signal,
        "rationale": rationale,
        "levels": levels,
        "indicators": indicators,
    }


def run_backtest(df: pd.DataFrame) -> dict:
    """Run a naive backtest based on the signal rules."""

    if df.empty:
        return {"trades": 0, "wins": 0, "losses": 0, "win_rate": 0}

    enriched = compute_indicators(df)
    trades = 0
    wins = 0
    losses = 0

    for idx in range(1, len(enriched)):
        slice_df = enriched.iloc[: idx + 1]
        indicators = summarize_indicators(slice_df)
        signal, _ = generate_signal(indicators)
        price_now = float(slice_df.iloc[-1]["close"])
        price_next = float(enriched.iloc[idx]["close"])
        if signal in {"BUY", "SELL"}:
            trades += 1
            if signal == "BUY" and price_next >= price_now:
                wins += 1
            elif signal == "SELL" and price_next <= price_now:
                wins += 1
            else:
                losses += 1

    win_rate = wins / trades if trades else 0
    return {"trades": trades, "wins": wins, "losses": losses, "win_rate": win_rate}
