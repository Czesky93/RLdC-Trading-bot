"""Report generation utilities."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from rldc.ai.summarizer import summarize
from rldc.config import AppConfig
from rldc.db.storage import Storage
from rldc.signals.engine import evaluate_signal, run_backtest


def generate_report(
    storage: Storage,
    config: AppConfig,
    pair: str,
    timeframe: str,
) -> dict:
    """Generate a JSON report for a given pair and timeframe."""

    df = storage.load_ohlcv(pair, timeframe)
    signal_data = evaluate_signal(df)
    summary = summarize({"pair": pair, "timeframe": timeframe, **signal_data}, config)
    backtest = run_backtest(df)

    report = {
        "pair": pair,
        "timeframe": timeframe,
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "signal": signal_data["signal"],
        "levels": signal_data["levels"],
        "indicators": signal_data["indicators"],
        "rationale": signal_data["rationale"],
        "summary": summary,
        "backtest": backtest,
        "disclaimer": "To nie jest porada inwestycyjna. Handel wiąże się z ryzykiem.",
    }

    return report


def write_report(report: dict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    _attach_log(output_dir)
    filename = f"{report['pair'].replace('/', '')}_{report['timeframe']}.json"
    path = output_dir / filename
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return path


def write_html_report(report: dict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    _attach_log(output_dir)
    filename = f"{report['pair'].replace('/', '')}_{report['timeframe']}.html"
    path = output_dir / filename
    html = f"""
    <html>
      <head><title>RLdC Report {report['pair']}</title></head>
      <body>
        <h1>RLdC Trading AiNalyzer Bot</h1>
        <p><strong>Pair:</strong> {report['pair']}</p>
        <p><strong>Timeframe:</strong> {report['timeframe']}</p>
        <p><strong>Signal:</strong> {report['signal']}</p>
        <p><strong>Levels:</strong> {report['levels']}</p>
        <p><strong>Summary:</strong> {report['summary']}</p>
        <p><em>{report['disclaimer']}</em></p>
      </body>
    </html>
    """
    path.write_text(html.strip())
    return path


def _attach_log(output_dir: Path) -> None:
    log_file = Path("log.txt")
    if log_file.exists():
        shutil.copy(log_file, output_dir / "log.txt")
