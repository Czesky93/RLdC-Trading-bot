"""SQLite storage backend for OHLCV and signals."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Iterable

import pandas as pd

from rldc.db.models import CREATE_OHLCV_TABLE, CREATE_SIGNAL_TABLE

logger = logging.getLogger(__name__)


class Storage:
    """SQLite storage for market data and signals."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_tables()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def _ensure_tables(self) -> None:
        with self._connect() as conn:
            conn.execute(CREATE_OHLCV_TABLE)
            conn.execute(CREATE_SIGNAL_TABLE)

    def insert_ohlcv(self, rows: Iterable[tuple]) -> int:
        query = (
            "INSERT OR IGNORE INTO ohlcv "
            "(exchange, pair, timeframe, timestamp, open, high, low, close, volume) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        with self._connect() as conn:
            cur = conn.executemany(query, rows)
            conn.commit()
            inserted = cur.rowcount if cur.rowcount is not None else 0
        logger.info("Inserted %s OHLCV rows", inserted)
        return inserted

    def insert_signal(self, row: tuple) -> None:
        query = (
            "INSERT OR REPLACE INTO signals "
            "(pair, timeframe, timestamp, signal, entry, stop_loss, take_profit, rationale) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        )
        with self._connect() as conn:
            conn.execute(query, row)
            conn.commit()

    def load_ohlcv(self, pair: str, timeframe: str) -> pd.DataFrame:
        query = (
            "SELECT timestamp, open, high, low, close, volume "
            "FROM ohlcv WHERE pair = ? AND timeframe = ? ORDER BY timestamp ASC"
        )
        with self._connect() as conn:
            df = pd.read_sql_query(query, conn, params=(pair, timeframe))
        return df

    def latest_signal(self, pair: str, timeframe: str) -> dict | None:
        query = (
            "SELECT timestamp, signal, entry, stop_loss, take_profit, rationale "
            "FROM signals WHERE pair = ? AND timeframe = ? ORDER BY timestamp DESC LIMIT 1"
        )
        with self._connect() as conn:
            cur = conn.execute(query, (pair, timeframe))
            row = cur.fetchone()
        if not row:
            return None
        return {
            "timestamp": row[0],
            "signal": row[1],
            "entry": row[2],
            "stop_loss": row[3],
            "take_profit": row[4],
            "rationale": row[5],
        }

    def export_to_csv(self, pair: str, timeframe: str, path: Path) -> Path:
        df = self.load_ohlcv(pair, timeframe)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        return path

    def export_to_parquet(self, pair: str, timeframe: str, path: Path) -> Path:
        df = self.load_ohlcv(pair, timeframe)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(path, index=False)
        return path
