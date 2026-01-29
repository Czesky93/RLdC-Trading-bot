"""Deep RL simulation stubs (experimental)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DeepRLReport:
    """Summary of a simulated RL training run."""

    episodes: int
    avg_reward: float
    note: str


def run_simulation(episodes: int = 50) -> DeepRLReport:
    """Simulate a lightweight Deep RL training loop.

    This does not execute real RL; it's a placeholder for future integration.
    """

    avg_reward = round(episodes * 0.01, 4)
    return DeepRLReport(
        episodes=episodes,
        avg_reward=avg_reward,
        note="Symulacja treningu RL (bez realnej polityki ani modeli).",
    )
