"""Self-improvement analyzer for logs and tests."""

from __future__ import annotations

from pathlib import Path

from rldc.self_improve.prompts import ERROR_ANALYSIS_PROMPT


def analyze_errors(error_log: Path) -> list[str]:
    """Analyze error logs and return improvement proposals."""

    if not error_log.exists():
        return ["Brak logów błędów do analizy."]

    content = error_log.read_text(encoding="utf-8")
    if not content.strip():
        return ["Log błędów jest pusty."]

    lines = content.splitlines()[-20:]
    proposals = [f"{ERROR_ANALYSIS_PROMPT} Ostatnie błędy: {lines}"]
    return proposals
