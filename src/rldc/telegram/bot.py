"""Telegram bot runner."""

from __future__ import annotations

import logging

from telegram.ext import Application, CommandHandler

from rldc.config import AppConfig
from rldc.telegram import handlers

logger = logging.getLogger(__name__)


def run_bot(config: AppConfig) -> None:
    """Run Telegram bot with configured handlers."""

    if not config.telegram_token:
        raise ValueError("Brak TELEGRAM_BOT_TOKEN w konfiguracji.")

    app = Application.builder().token(config.telegram_token).build()
    app.bot_data["config"] = config

    app.add_handler(CommandHandler("status", handlers.status))
    app.add_handler(CommandHandler("pairs", handlers.pairs))
    app.add_handler(CommandHandler("analyze", handlers.analyze))
    app.add_handler(CommandHandler("report", handlers.report))
    app.add_handler(CommandHandler("top10", handlers.top10))

    logger.info("Telegram bot started")
    app.run_polling()
