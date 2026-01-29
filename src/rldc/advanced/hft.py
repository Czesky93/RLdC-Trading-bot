"""High-Frequency Trading (HFT) simulator (experimental)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class HFTMetrics:
    """Simple metrics for a simulated HFT loop."""

    orders_simulated: int
    avg_latency_ms: float
    note: str


def simulate_hft(orders: int = 1000) -> HFTMetrics:
    """Simulate an HFT loop with mocked latency metrics.

    No real exchange trading is performed.
    """

    avg_latency_ms = max(0.2, 10_000 / max(orders, 1))
    return HFTMetrics(
        orders_simulated=orders,
        avg_latency_ms=avg_latency_ms,
        note="Symulacja HFT (bez realnych zleceń).",
    )
