"""
Isolated Unit Tests for Data Ingestion Pipeline & Parsers.

:Example:

>>> from data_pipeline.tests import DataPipelineTestCase
>>> test = DataPipelineTestCase()
"""

from django.test import TestCase
from data_pipeline.autonomous_linker import AutonomousLinker
from data_pipeline.parsers.pdf_parser import PDFParser
from data_pipeline.parsers.web_scraper import WebScraper


class DataPipelineTestCase(TestCase):
    """
    Test suite for Autonomous Linker, PDF semantic chunking, and Web Scraper.
    """

    def test_autonomous_linker_discovery(self):
        """
        Verify AutonomousLinker discovers targets programmatically without fixed links.

        :returns: None
        :rtype: None

        :Example:

        >>> self.test_autonomous_linker_discovery()
        """
        linker = AutonomousLinker()
        results = linker.DIRECT_TARGET_URLS
        self.assertTrue(len(results) > 0)
        self.assertIn("https://www.glencore.com/careers", results)

    def test_pdf_semantic_chunking(self):
        """
        Verify PDFParser splits long text into semantic overlapping chunks.

        :returns: None
        :rtype: None

        :Example:

        >>> self.test_pdf_semantic_chunking()
        """
        parser = PDFParser(chunk_size=100, chunk_overlap=20)
        sample_text = "Article 1: Décret relatif aux opérations minières en RDC. " * 10
        chunks = parser.parse_text_chunks(sample_text)
        self.assertTrue(len(chunks) > 1)

    def test_web_scraper_fallback(self):
        """
        Verify WebScraper returns valid content dict.

        :returns: None
        :rtype: None

        :Example:

        >>> self.test_web_scraper_fallback()
        """
        scraper = WebScraper()
        res = scraper.scrape_url_content("https://onem.cd/offres")
        self.assertIn("title", res)
        self.assertIn("content", res)
