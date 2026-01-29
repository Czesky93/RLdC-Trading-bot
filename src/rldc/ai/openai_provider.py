"""OpenAI provider for summaries."""

from __future__ import annotations

import logging

from openai import OpenAI

from rldc.ai.provider_base import AIProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    """OpenAI summary provider."""

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def summarize(self, payload: dict) -> str:
        client = OpenAI(api_key=self.api_key)
        prompt = (
            "Jesteś asystentem analizy rynku. Na podstawie danych: "
            f"{payload}. Podaj krótkie, probabilistyczne streszczenie. "
            "Zawsze dodaj zastrzeżenie o ryzyku."
        )
        try:
            response = client.responses.create(
                model=self.model,
                input=[{"role": "user", "content": prompt}],
            )
        except Exception as exc:  # pragma: no cover - network
            logger.error("OpenAI error: %s", exc)
            return "Nie udało się pobrać streszczenia OpenAI."

        text_parts: list[str] = []
        for item in response.output:
            if hasattr(item, "content"):
                for content in item.content:
                    if hasattr(content, "text"):
                        text_parts.append(content.text)
        return " ".join(text_parts) or "Brak odpowiedzi OpenAI."
