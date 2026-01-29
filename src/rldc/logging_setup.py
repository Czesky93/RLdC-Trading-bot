"""Logging configuration for RLdC Trading AiNalyzer Bot."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from rldc.config import AppConfig


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def setup_logging(config: AppConfig) -> None:
    """Configure logging with rotating file handlers."""

    config.log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    formatter = logging.Formatter(LOG_FORMAT)

    app_handler = RotatingFileHandler(
        config.log_dir / "app.log", maxBytes=2_000_000, backupCount=3
    )
    app_handler.setFormatter(formatter)

    error_handler = RotatingFileHandler(
        config.log_dir / "error.log", maxBytes=1_000_000, backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root.handlers.clear()
    root.addHandler(app_handler)
    root.addHandler(error_handler)
    root.addHandler(console_handler)
