"""
App configuration for analyzer module.

Initializes the APScheduler background scheduler on app startup to trigger
the autonomous data ingestion pipeline at 00:00 and 12:00 daily.

:Example:

>>> from analyzer.apps import AnalyzerConfig
>>> print(AnalyzerConfig.name)
'analyzer'
"""

import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class AnalyzerConfig(AppConfig):
    """
    Django AppConfig for analyzer application.

    Starts the APScheduler cron job on server startup to run the scraping pipeline
    every day at midnight (00:00) and noon (12:00).
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "analyzer"

    def ready(self):
        """
        Hook called when the Django app registry is fully populated.

        Starts the APScheduler with two CronTrigger jobs:
        - 00:00 daily
        - 12:00 daily

        :returns: None
        :rtype: None

        :Example:

        >>> # Automatically called by Django on startup
        >>> # Equivalent to:
        >>> config = AnalyzerConfig("analyzer", None)
        >>> config.ready()
        """
        import sys

        # Do not start scheduler in management commands (except runserver)
        # to avoid double-running in Django's auto-reloader
        if "runserver" not in sys.argv and "run_scraping_pipeline" not in sys.argv:
            return

        # Avoid starting the scheduler twice in Django's dev auto-reloader
        if any(arg in sys.argv for arg in ["--noreload"]) or self._is_main_process():
            self._start_scheduler()

    def _is_main_process(self) -> bool:
        """
        Detect whether we are in the main Django process (not the auto-reload watcher).

        :returns: True if this is the main process.
        :rtype: bool
        """
        import os
        return os.environ.get("RUN_MAIN") == "true"

    def _start_scheduler(self):
        """
        Initialize and start the APScheduler with bi-daily cron triggers.

        :returns: None
        :rtype: None
        """
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.cron import CronTrigger

            scheduler = BackgroundScheduler(timezone="Africa/Lubumbashi")

            def _run_pipeline():
                """Execute the scraping pipeline safely from the scheduler thread."""
                try:
                    logger.info("[Scheduler] Triggering bi-daily scraping pipeline...")
                    from data_pipeline.cron_orchestrator import CronOrchestrator
                    orchestrator = CronOrchestrator()
                    orchestrator.run_pipeline()
                    logger.info("[Scheduler] Bi-daily pipeline completed.")
                except Exception as exc:
                    logger.error(f"[Scheduler] Pipeline error: {exc}")

            # Trigger at 00:00 every day
            scheduler.add_job(
                _run_pipeline,
                trigger=CronTrigger(hour=0, minute=0),
                id="mayele_scraping_midnight",
                name="Mayele IA — Ingestion Minuit (00h00)",
                replace_existing=True,
            )

            # Trigger at 12:00 every day
            scheduler.add_job(
                _run_pipeline,
                trigger=CronTrigger(hour=12, minute=0),
                id="mayele_scraping_noon",
                name="Mayele IA — Ingestion Midi (12h00)",
                replace_existing=True,
            )

            scheduler.start()
            logger.info(
                "[Scheduler] APScheduler started — pipeline scheduled at 00:00 and 12:00 daily (Africa/Lubumbashi)"
            )

        except ImportError:
            logger.warning("[Scheduler] APScheduler not installed. Run: pip install apscheduler")
        except Exception as exc:
            logger.error(f"[Scheduler] Failed to start scheduler: {exc}")
