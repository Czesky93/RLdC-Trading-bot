"""Exchange client wrapper (read-only)."""

from __future__ import annotations

import logging
from typing import Any

import ccxt

logger = logging.getLogger(__name__)


class ExchangeClient:
    """Simple CCXT client for read-only market data."""

    def __init__(self, exchange_name: str = "binance") -> None:
        self.exchange_name = exchange_name
        self._exchange = self._init_exchange()

    def _init_exchange(self) -> ccxt.Exchange:
        exchange_class = getattr(ccxt, self.exchange_name)
        exchange = exchange_class({"enableRateLimit": True, "options": {"defaultType": "spot"}})
        logger.info("Initialized exchange client: %s", self.exchange_name)
        return exchange

    def fetch_ohlcv(self, pair: str, timeframe: str, limit: int = 500) -> list[list[Any]]:
        """Fetch OHLCV data for a pair/timeframe."""

        return self._exchange.fetch_ohlcv(pair, timeframe=timeframe, limit=limit)
