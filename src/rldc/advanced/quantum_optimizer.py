"""Quantum-inspired optimization (experimental, offline)."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class QuantumOptimizationResult:
    """Result of a quantum-inspired optimization pass."""

    best_score: float
    best_weights: list[float]
    note: str


def optimize_weights(seed: int = 42, steps: int = 200) -> QuantumOptimizationResult:
    """Run a simple simulated annealing-like search for indicator weights.

    This is a lightweight, heuristic placeholder and does NOT guarantee performance.
    """

    rng = np.random.default_rng(seed)
    weights = rng.uniform(0.1, 1.0, size=4)
    best_weights = weights.copy()
    best_score = _score(weights)

    temperature = 1.0
    for _ in range(steps):
        candidate = weights + rng.normal(0, 0.05, size=weights.shape)
        candidate = np.clip(candidate, 0.01, 2.0)
        score = _score(candidate)
        if score > best_score or rng.random() < math.exp((score - best_score) / temperature):
            weights = candidate
            if score > best_score:
                best_score = score
                best_weights = candidate.copy()
        temperature = max(temperature * 0.98, 0.01)

    return QuantumOptimizationResult(
        best_score=float(best_score),
        best_weights=best_weights.tolist(),
        note="Heurystyczna optymalizacja (nie jest to realne QA/QPU).",
    )


def _score(weights: np.ndarray) -> float:
    return float(np.tanh(np.sum(weights) / len(weights)))
