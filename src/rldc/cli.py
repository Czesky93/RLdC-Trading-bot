"""CLI entrypoint for RLdC Trading AiNalyzer Bot."""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path

import typer

from rldc.config import AppConfig
from rldc.data.exchange_client import ExchangeClient
from rldc.data.ohlcv_fetcher import fetch_and_store
from rldc.db.storage import Storage
from rldc.logging_setup import setup_logging
from rldc.reports.generator import generate_report, write_html_report, write_report
from rldc.scheduler.scheduler import start_scheduler
from rldc.self_improve.analyzer import analyze_errors
from rldc.telegram.bot import run_bot
from rldc.web.app import create_app

app = typer.Typer(add_completion=False)
logger = logging.getLogger(__name__)


@app.callback()
def main() -> None:
    """RLdC Trading AiNalyzer Bot CLI."""


@app.command()
def status() -> None:
    """Show current configuration status."""
    config = AppConfig.load()
    setup_logging(config)
    typer.echo(f"RLdC AiNalyzer Bot v{config.app_env} | DB: {config.db_path}")


@app.command()
def fetch(pair: str = "BTC/USDT", timeframe: str = "1h", limit: int = 500) -> None:
    """Fetch OHLCV data and store it in SQLite."""
    config = AppConfig.load()
    setup_logging(config)
    storage = Storage(config.db_path)
    exchange = ExchangeClient()
    inserted = fetch_and_store(storage, exchange, pair, timeframe, limit)
    typer.echo(f"Inserted {inserted} rows for {pair} {timeframe}.")


@app.command()
def analyze(pair: str = "BTC/USDT", timeframe: str = "1h") -> None:
    """Analyze a pair/timeframe and print report."""
    config = AppConfig.load()
    setup_logging(config)
    storage = Storage(config.db_path)
    report = generate_report(storage, config, pair, timeframe)
    typer.echo(json.dumps(report, indent=2, ensure_ascii=False))


@app.command()
def report(
    pair: str = "BTC/USDT",
    timeframe: str = "1h",
    html: bool = False,
) -> None:
    """Generate and save report to disk."""
    config = AppConfig.load()
    setup_logging(config)
    storage = Storage(config.db_path)
    report_data = generate_report(storage, config, pair, timeframe)
    path = write_report(report_data, config.report_dir)
    typer.echo(f"Report saved: {path}")
    if html:
        html_path = write_html_report(report_data, config.report_dir)
        typer.echo(f"HTML report saved: {html_path}")


@app.command()
def run() -> None:
    """Run scheduler loop."""
    config = AppConfig.load()
    setup_logging(config)
    start_scheduler(config)


@app.command()
def web(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run FastAPI web server."""
    config = AppConfig.load()
    setup_logging(config)
    import uvicorn

    app_instance = create_app(config)
    uvicorn.run(app_instance, host=host, port=port)


@app.command()
def telegram() -> None:
    """Run Telegram bot."""
    config = AppConfig.load()
    setup_logging(config)
    run_bot(config)


@app.command()
def self_improve() -> None:
    """Analyze logs and print improvement proposals."""
    config = AppConfig.load()
    setup_logging(config)
    proposals = analyze_errors(config.log_dir / "error.log")
    typer.echo("\n".join(proposals))


@app.command()
def export(
    pair: str = "BTC/USDT", timeframe: str = "1h", fmt: str = "csv", output_dir: Path = Path("exports")
) -> None:
    """Export OHLCV data to CSV or Parquet."""
    config = AppConfig.load()
    setup_logging(config)
    storage = Storage(config.db_path)
    filename = f"{pair.replace('/', '')}_{timeframe}.{fmt}"
    path = output_dir / filename
    if fmt == "parquet":
        storage.export_to_parquet(pair, timeframe, path)
    else:
        storage.export_to_csv(pair, timeframe, path)
    if Path("log.txt").exists():
        shutil.copy("log.txt", output_dir / "log.txt")
    typer.echo(f"Exported to {path}")
