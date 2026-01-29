"""GitHub PR helper for self-improvement proposals."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from rldc.config import AppConfig

logger = logging.getLogger(__name__)


def create_pull_request(config: AppConfig, title: str, body: str, head: str, base: str = "main") -> dict[str, Any]:
    """Create a pull request using GitHub API.

    Requires GITHUB_TOKEN and GITHUB_REPO (e.g. owner/repo).
    """

    if not config.github_token or not config.github_repo:
        raise ValueError("Brak konfiguracji GitHub (GITHUB_TOKEN / GITHUB_REPO).")

    url = f"https://api.github.com/repos/{config.github_repo}/pulls"
    headers = {
        "Authorization": f"Bearer {config.github_token}",
        "Accept": "application/vnd.github+json",
    }
    payload = {"title": title, "body": body, "head": head, "base": base}

    response = httpx.post(url, headers=headers, json=payload, timeout=30)
    if response.status_code >= 300:
        logger.error("GitHub PR failed: %s", response.text)
        raise RuntimeError("GitHub PR creation failed")

    return response.json()
