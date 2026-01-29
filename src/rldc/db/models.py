"""Database schema definitions."""

from __future__ import annotations

CREATE_OHLCV_TABLE = """
CREATE TABLE IF NOT EXISTS ohlcv (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exchange TEXT NOT NULL,
    pair TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    UNIQUE(exchange, pair, timeframe, timestamp)
);
"""

CREATE_SIGNAL_TABLE = """
CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    signal TEXT NOT NULL,
    entry REAL,
    stop_loss REAL,
    take_profit REAL,
    rationale TEXT,
    UNIQUE(pair, timeframe, timestamp)
);
"""
