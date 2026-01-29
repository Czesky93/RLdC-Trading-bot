"""AI provider base classes."""

from __future__ import annotations

from typing import Protocol


class AIProvider(Protocol):
    """Protocol for AI providers."""

    def summarize(self, payload: dict) -> str:
        ...
