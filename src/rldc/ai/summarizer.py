"""AI summarization entrypoint."""

from __future__ import annotations

from rldc.ai.heuristic_provider import HeuristicProvider
from rldc.ai.openai_provider import OpenAIProvider
from rldc.config import AppConfig


def build_provider(config: AppConfig):
    """Select provider based on config."""

    if config.openai_api_key:
        return OpenAIProvider(config.openai_api_key, config.openai_model)
    return HeuristicProvider()


def summarize(payload: dict, config: AppConfig) -> str:
    provider = build_provider(config)
    return provider.summarize(payload)
