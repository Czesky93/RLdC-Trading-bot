import statistics
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests

BINANCE_BASE_URL = "https://api.binance.com"

DEFAULT_RULES = {
    "INTERVAL": "1m",
    "FAST_SMA": 9,
    "SLOW_SMA": 21,
    "RSI_PERIOD": 14,
    "RSI_BUY_MIN": 50,
    "RSI_BUY_MAX": 70,
    "RSI_SELL_MIN": 30,
    "RSI_SELL_MAX": 50,
    "ORDERBOOK_IMBALANCE_BUY": 0.1,
    "ORDERBOOK_IMBALANCE_SELL": -0.1,
    "VOLUME_SPIKE_MULTIPLIER": 1.5,
    "MIN_SIGNAL_SCORE": 2,
}

@dataclass
class SignalResult:
    symbol: str
    action: str
    score: int
    reasons: List[str]
    last_price: float
    timestamp: int


def fetch_klines(symbol: str, interval: str, limit: int = 200) -> List[Dict[str, float]]:
    response = requests.get(
        f"{BINANCE_BASE_URL}/api/v3/klines",
        params={"symbol": symbol, "interval": interval, "limit": limit},
        timeout=10,
    )
    response.raise_for_status()
    klines = response.json()
    parsed = []
    for k in klines:
        parsed.append(
            {
                "open_time": int(k[0]),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
            }
        )
    return parsed


def fetch_orderbook_imbalance(symbol: str, limit: int = 100) -> float:
    response = requests.get(
        f"{BINANCE_BASE_URL}/api/v3/depth",
        params={"symbol": symbol, "limit": limit},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    bids = sum(float(bid[1]) for bid in data.get("bids", []))
    asks = sum(float(ask[1]) for ask in data.get("asks", []))
    total = bids + asks
    if total == 0:
        return 0.0
    return (bids - asks) / total


def simple_moving_average(values: List[float], window: int) -> Optional[float]:
    if len(values) < window:
        return None
    return statistics.fmean(values[-window:])


def rsi(values: List[float], period: int = 14) -> Optional[float]:
    if len(values) < period + 1:
        return None
    gains = []
    losses = []
    for i in range(-period, 0):
        delta = values[i] - values[i - 1]
        if delta >= 0:
            gains.append(delta)
        else:
            losses.append(abs(delta))
    avg_gain = statistics.fmean(gains) if gains else 0.0
    avg_loss = statistics.fmean(losses) if losses else 0.0
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def volume_spike(volumes: List[float], multiplier: float) -> bool:
    if len(volumes) < 2:
        return False
    baseline = statistics.fmean(volumes[:-1])
    if baseline == 0:
        return False
    return volumes[-1] >= baseline * multiplier


def build_signal(
    symbol: str,
    interval: str,
    rules: Dict[str, float],
) -> SignalResult:
    merged_rules = {**DEFAULT_RULES, **(rules or {})}
    klines = fetch_klines(symbol, interval)
    closes = [k["close"] for k in klines]
    volumes = [k["volume"] for k in klines]
    last_price = closes[-1]
    last_timestamp = klines[-1]["open_time"]

    fast_sma = simple_moving_average(closes, int(merged_rules["FAST_SMA"]))
    slow_sma = simple_moving_average(closes, int(merged_rules["SLOW_SMA"]))
    current_rsi = rsi(closes, int(merged_rules["RSI_PERIOD"]))
    imbalance = fetch_orderbook_imbalance(symbol)
    has_volume_spike = volume_spike(volumes, float(merged_rules["VOLUME_SPIKE_MULTIPLIER"]))

    score = 0
    reasons = []

    if fast_sma is not None and slow_sma is not None:
        if fast_sma > slow_sma:
            score += 1
            reasons.append("SMA: trend wzrostowy")
        elif fast_sma < slow_sma:
            score -= 1
            reasons.append("SMA: trend spadkowy")

    if current_rsi is not None:
        if merged_rules["RSI_BUY_MIN"] <= current_rsi <= merged_rules["RSI_BUY_MAX"]:
            score += 1
            reasons.append("RSI: momentum byczy")
        elif merged_rules["RSI_SELL_MIN"] <= current_rsi <= merged_rules["RSI_SELL_MAX"]:
            score -= 1
            reasons.append("RSI: momentum niedźwiedzi")

    if imbalance >= float(merged_rules["ORDERBOOK_IMBALANCE_BUY"]):
        score += 1
        reasons.append("Order book: przewaga bidów")
    elif imbalance <= float(merged_rules["ORDERBOOK_IMBALANCE_SELL"]):
        score -= 1
        reasons.append("Order book: przewaga asków")

    if has_volume_spike:
        score += 1
        reasons.append("Wolumen: wzmożony obrót")

    min_score = int(merged_rules["MIN_SIGNAL_SCORE"])
    if score >= min_score:
        action = "BUY"
    elif score <= -min_score:
        action = "SELL"
    else:
        action = "HOLD"

    return SignalResult(
        symbol=symbol,
        action=action,
        score=score,
        reasons=reasons,
        last_price=last_price,
        timestamp=last_timestamp,
    )
