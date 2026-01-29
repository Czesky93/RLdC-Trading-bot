"""Predictive AI module (experimental)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PredictiveSummary:
    """Summary for predictive signals."""

    confidence: float
    horizon: str
    note: str


def generate_prediction(horizon: str = "24h") -> PredictiveSummary:
    """Generate a probabilistic prediction placeholder.

    The output is a stub and must not be treated as advice.
    """

    return PredictiveSummary(
        confidence=0.45,
        horizon=horizon,
        note="Heurystyczna predykcja (probabilistyczna, bez gwarancji).",
    )
