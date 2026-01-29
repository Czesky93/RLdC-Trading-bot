"""Blockchain analysis (experimental, offline)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class BlockchainInsight:
    """Lightweight blockchain analysis result."""

    anomalies_found: int
    note: str


def analyze_blockchain(transactions_checked: int = 0) -> BlockchainInsight:
    """Analyze blockchain data in a placeholder mode.

    No external calls are made; this is a stub for future integrations.
    """

    anomalies_found = 0 if transactions_checked < 1000 else 1
    return BlockchainInsight(
        anomalies_found=anomalies_found,
        note="Analiza blockchain offline (stub, bez realnych danych).",
    )
