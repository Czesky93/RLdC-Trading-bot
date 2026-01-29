"""Scheduler jobs for RLdC Trading AiNalyzer Bot."""

from __future__ import annotations

import logging

from rldc.config import AppConfig
from rldc.data.exchange_client import ExchangeClient
from rldc.data.ohlcv_fetcher import fetch_and_store
from rldc.db.storage import Storage
from rldc.reports.generator import generate_report, write_report
from rldc.signals.engine import evaluate_signal

logger = logging.getLogger(__name__)


def analyze_pair(storage: Storage, config: AppConfig, pair: str, timeframe: str) -> dict:
    """Fetch data, compute signal, save report, and store signal."""

    exchange = ExchangeClient()
    fetch_and_store(storage, exchange, pair, timeframe)
    df = storage.load_ohlcv(pair, timeframe)
    signal = evaluate_signal(df)
    storage.insert_signal(
        (
            pair,
            timeframe,
            signal["timestamp"],
            signal["signal"],
            signal["levels"]["entry"],
            signal["levels"]["stop_loss"],
            signal["levels"]["take_profit"],
            signal["rationale"],
        )
    )
    report = generate_report(storage, config, pair, timeframe)
    write_report(report, config.report_dir)
    return report


def scheduled_run(config: AppConfig) -> None:
    """Run analysis for all configured pairs/timeframes."""

    storage = Storage(config.db_path)
    for pair in config.default_pairs:
        for timeframe in config.default_timeframes:
            try:
                analyze_pair(storage, config, pair, timeframe)
            except Exception as exc:  # pragma: no cover
                logger.error("Analysis failed for %s %s: %s", pair, timeframe, exc)
