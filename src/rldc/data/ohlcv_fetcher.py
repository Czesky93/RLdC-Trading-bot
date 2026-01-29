"""OHLCV fetcher with validation and storage."""

from __future__ import annotations

import logging
from typing import Iterable

from rldc.data.exchange_client import ExchangeClient
from rldc.db.storage import Storage

logger = logging.getLogger(__name__)


def fetch_and_store(
    storage: Storage,
    exchange: ExchangeClient,
    pair: str,
    timeframe: str,
    limit: int = 500,
) -> int:
    """Fetch OHLCV from exchange and store idempotently."""

    raw = exchange.fetch_ohlcv(pair, timeframe=timeframe, limit=limit)
    rows = _validate_rows(raw, exchange.exchange_name, pair, timeframe)
    return storage.insert_ohlcv(rows)


def _validate_rows(
    rows: Iterable[list[float]], exchange: str, pair: str, timeframe: str
) -> list[tuple]:
    cleaned: list[tuple] = []
    for row in rows:
        if len(row) < 6:
            logger.warning("Skipping malformed row: %s", row)
            continue
        ts, open_, high, low, close, volume = row[:6]
        if any(value is None for value in (ts, open_, high, low, close, volume)):
            continue
        cleaned.append((exchange, pair, timeframe, int(ts), float(open_), float(high), float(low), float(close), float(volume)))
    return cleaned
