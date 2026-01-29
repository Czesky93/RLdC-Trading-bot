"""Configuration loader for RLdC Trading AiNalyzer Bot."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv

PRIMARY_ENV_PATH = Path("/home/oem/rldc_full_setup/config/.env")
FALLBACK_ENV_PATH = Path(".env")


@dataclass(slots=True)
class AppConfig:
    """Application configuration loaded from environment variables."""

    app_env: str
    log_dir: Path
    data_dir: Path
    db_path: Path
    report_dir: Path
    default_pairs: list[str]
    default_timeframes: list[str]
    scheduler_interval_minutes: int
    telegram_token: str | None
    telegram_chat_id: str | None
    openai_api_key: str | None
    openai_model: str
    github_token: str | None
    github_repo: str | None

    @classmethod
    def load(cls) -> "AppConfig":
        """Load configuration from environment variables and .env files."""

        _load_env_files([PRIMARY_ENV_PATH, FALLBACK_ENV_PATH])

        data_dir = Path(os.getenv("RLDC_DATA_DIR", "data_store")).resolve()
        log_dir = Path(os.getenv("RLDC_LOG_DIR", "logs")).resolve()
        report_dir = Path(os.getenv("RLDC_REPORT_DIR", "reports_out")).resolve()
        db_path = Path(os.getenv("RLDC_DB_PATH", str(data_dir / "rldc.sqlite"))).resolve()

        default_pairs = _split_csv(
            os.getenv("RLDC_PAIRS", "BTC/USDT,ETH/USDT")
        )
        default_timeframes = _split_csv(
            os.getenv("RLDC_TIMEFRAMES", "1m,15m,1h,6h,12h,1w,1M")
        )

        return cls(
            app_env=os.getenv("RLDC_ENV", "dev"),
            log_dir=log_dir,
            data_dir=data_dir,
            db_path=db_path,
            report_dir=report_dir,
            default_pairs=default_pairs,
            default_timeframes=default_timeframes,
            scheduler_interval_minutes=int(os.getenv("RLDC_SCHEDULER_MINUTES", "15")),
            telegram_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            github_token=os.getenv("GITHUB_TOKEN"),
            github_repo=os.getenv("GITHUB_REPO"),
        )


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _load_env_files(paths: Iterable[Path]) -> None:
    for path in paths:
        if path.exists():
            load_dotenv(path, override=False)
