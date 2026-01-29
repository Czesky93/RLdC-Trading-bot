"""APScheduler wrapper."""

from __future__ import annotations

import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from rldc.config import AppConfig
from rldc.scheduler.jobs import scheduled_run

logger = logging.getLogger(__name__)


def start_scheduler(config: AppConfig) -> None:
    """Start the blocking scheduler."""

    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        scheduled_run,
        "interval",
        minutes=config.scheduler_interval_minutes,
        args=[config],
        id="rldc_analysis",
        replace_existing=True,
    )
    logger.info("Scheduler started with interval %s minutes", config.scheduler_interval_minutes)
    scheduler.start()
