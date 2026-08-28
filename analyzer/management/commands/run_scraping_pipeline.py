"""
Django management command: run_scraping_pipeline

Trigger the full autonomous scraping pipeline manually or via scheduler.

Usage:
    ./venv/bin/python manage.py run_scraping_pipeline

:Example:

>>> # From Django shell
>>> from django.core.management import call_command
>>> call_command("run_scraping_pipeline")
"""

from django.core.management.base import BaseCommand
from data_pipeline.cron_orchestrator import CronOrchestrator


class Command(BaseCommand):
    """
    Management command to trigger the full ingestion pipeline.
    """
    help = "Run the bi-daily autonomous web scraping and data ingestion pipeline."

    def handle(self, *args, **options):
        """
        Execute the full scraping and ingestion wave.

        :returns: None
        :rtype: None
        """
        self.stdout.write(self.style.NOTICE("[Mayele IA] Starting scraping pipeline..."))
        try:
            orchestrator = CronOrchestrator()
            success = orchestrator.run_pipeline()
            if success:
                self.stdout.write(self.style.SUCCESS("[Mayele IA] Pipeline completed successfully."))
            else:
                self.stdout.write(self.style.WARNING("[Mayele IA] Pipeline completed with no items ingested."))
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"[Mayele IA] Pipeline error: {exc}"))
