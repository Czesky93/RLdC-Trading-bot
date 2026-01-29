"""Heuristic AI provider (offline)."""

from __future__ import annotations

from rldc.ai.provider_base import AIProvider


class HeuristicProvider(AIProvider):
    """Simple heuristic summary provider."""

    def summarize(self, payload: dict) -> str:
        indicators = payload.get("indicators", {})
        signal = payload.get("signal", "WAIT")
        rsi = indicators.get("rsi", 0)
        macd = indicators.get("macd", 0)
        macd_signal = indicators.get("macd_signal", 0)

        summary = (
            f"Sygnał: {signal}. RSI={rsi:.2f}, MACD={macd:.4f} vs signal={macd_signal:.4f}. "
            "To jest heurystyczna analiza, nie gwarantuje zysków."
        )
        return summary
