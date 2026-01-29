from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional

from trading.signal_engine import build_signal, fetch_klines, rsi, simple_moving_average


@dataclass
class RiskConfig:
    risk_per_trade_pct: Decimal = Decimal("1.0")
    max_position_pct: Decimal = Decimal("10.0")
    atr_period: int = 14
    atr_multiplier_sl: Decimal = Decimal("1.5")
    atr_multiplier_tp: Decimal = Decimal("3.0")
    min_signal_score: int = 2


@dataclass
class TradePlan:
    symbol: str
    action: str
    score: int
    order_size_usdt: Decimal
    stop_loss: Optional[Decimal]
    take_profit: Optional[Decimal]
    reasons: List[str]


def _calculate_atr(klines: List[Dict[str, float]], period: int) -> Optional[Decimal]:
    if len(klines) < period + 1:
        return None
    trs: List[Decimal] = []
    for i in range(-period, 0):
        high = Decimal(str(klines[i]["high"]))
        low = Decimal(str(klines[i]["low"]))
        prev_close = Decimal(str(klines[i - 1]["close"]))
        true_range = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(true_range)
    if not trs:
        return None
    return sum(trs) / Decimal(len(trs))


def build_trade_plan(
    symbol: str,
    interval: str,
    rules: Dict[str, float],
    risk: RiskConfig,
    available_quote: Decimal,
) -> TradePlan:
    signal = build_signal(symbol, interval, rules)
    klines = fetch_klines(symbol, interval)
    closes = [k["close"] for k in klines]

    fast_sma = simple_moving_average(closes, int(rules.get("FAST_SMA", 9)))
    slow_sma = simple_moving_average(closes, int(rules.get("SLOW_SMA", 21)))
    current_rsi = rsi(closes, int(rules.get("RSI_PERIOD", 14)))
    atr = _calculate_atr(klines, risk.atr_period)

    reasons = list(signal.reasons)
    if current_rsi is not None:
        reasons.append(f"RSI: {current_rsi:.2f}")

    action = signal.action
    if fast_sma is not None and slow_sma is not None:
        if action == "BUY" and fast_sma < slow_sma:
            action = "HOLD"
            reasons.append("Filtr trendu: brak potwierdzenia wzrostowego")
        elif action == "SELL" and fast_sma > slow_sma:
            action = "HOLD"
            reasons.append("Filtr trendu: brak potwierdzenia spadkowego")

    last_price = Decimal(str(signal.last_price))
    if signal.score < risk.min_signal_score and signal.score > -risk.min_signal_score:
        action = "HOLD"
        reasons.append("Sygnal zbyt słaby względem min_signal_score")

    stop_loss = None
    take_profit = None
    order_size_usdt = Decimal("0")

    if action in {"BUY", "SELL"} and atr is not None and atr > 0:
        risk_amount = available_quote * (risk.risk_per_trade_pct / Decimal("100"))
        stop_loss_distance = atr * risk.atr_multiplier_sl
        max_position_value = available_quote * (risk.max_position_pct / Decimal("100"))
        if stop_loss_distance > 0:
            order_size_usdt = min(risk_amount / stop_loss_distance * last_price, max_position_value)
            if action == "BUY":
                stop_loss = last_price - stop_loss_distance
                take_profit = last_price + (atr * risk.atr_multiplier_tp)
            else:
                stop_loss = last_price + stop_loss_distance
                take_profit = last_price - (atr * risk.atr_multiplier_tp)
    else:
        reasons.append("Brak ATR do wyliczenia ryzyka/pozycji")

    return TradePlan(
        symbol=symbol,
        action=action,
        score=signal.score,
        order_size_usdt=order_size_usdt,
        stop_loss=stop_loss,
        take_profit=take_profit,
        reasons=reasons,
    )
