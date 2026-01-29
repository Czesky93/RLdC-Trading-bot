"""Telegram handlers."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from rldc.config import AppConfig
from rldc.db.storage import Storage
from rldc.reports.generator import generate_report
from rldc.scheduler.jobs import analyze_pair

logger = logging.getLogger(__name__)


def _storage(config: AppConfig) -> Storage:
    return Storage(config.db_path)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    config: AppConfig = context.bot_data["config"]
    await update.message.reply_text(f"RLdC AiNalyzer Bot działa. ENV={config.app_env}.")


async def pairs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    config: AppConfig = context.bot_data["config"]
    await update.message.reply_text(", ".join(config.default_pairs))


async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    config: AppConfig = context.bot_data["config"]
    if not context.args:
        await update.message.reply_text("Użycie: /analyze BTC/USDT 1h")
        return
    pair = context.args[0]
    timeframe = context.args[1] if len(context.args) > 1 else "1h"
    storage = _storage(config)
    report = analyze_pair(storage, config, pair, timeframe)
    await update.message.reply_text(
        f"{pair} {timeframe}: {report['signal']} | {report['summary']}"
    )


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    config: AppConfig = context.bot_data["config"]
    if not context.args:
        await update.message.reply_text("Użycie: /report BTC/USDT 1h")
        return
    pair = context.args[0]
    timeframe = context.args[1] if len(context.args) > 1 else "1h"
    storage = _storage(config)
    report_data = generate_report(storage, config, pair, timeframe)
    await update.message.reply_text(str(report_data))


async def top10(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    config: AppConfig = context.bot_data["config"]
    top = config.default_pairs[:10]
    await update.message.reply_text("Top 10 par: " + ", ".join(top))
