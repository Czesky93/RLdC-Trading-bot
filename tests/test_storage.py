from pathlib import Path

from rldc.db.storage import Storage


def test_storage_insert_and_load(tmp_path: Path):
    db_path = tmp_path / "test.sqlite"
    storage = Storage(db_path)
    rows = [
        ("binance", "BTC/USDT", "1h", 1, 1, 1, 1, 1, 10),
        ("binance", "BTC/USDT", "1h", 2, 2, 2, 2, 2, 20),
    ]
    storage.insert_ohlcv(rows)
    df = storage.load_ohlcv("BTC/USDT", "1h")
    assert len(df) == 2
