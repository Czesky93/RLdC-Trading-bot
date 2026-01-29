"""Risk management helpers."""

from __future__ import annotations


def compute_levels(price: float, signal: str, risk_pct: float = 0.02) -> dict[str, float | None]:
    """Compute entry, stop-loss, and take-profit levels.

    Uses a conservative fixed percentage by default.
    """

    if price <= 0:
        return {"entry": None, "stop_loss": None, "take_profit": None}

    if signal == "BUY":
        return {
            "entry": price,
            "stop_loss": price * (1 - risk_pct),
            "take_profit": price * (1 + risk_pct * 2),
        }
    if signal == "SELL":
        return {
            "entry": price,
            "stop_loss": price * (1 + risk_pct),
            "take_profit": price * (1 - risk_pct * 2),
        }
    return {"entry": price, "stop_loss": None, "take_profit": None}
