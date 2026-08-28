#!/usr/bin/env python3
"""
Test Suite for Web Scraping and Markdown Cleaning in Mayele IA.

Verifies that raw '###' headers are stripped from responses and tests
web scraping capabilities across Village Afrique, MediaCongo, and global sites.

:Example:

>>> python bin/test_web_scraper.py
"""

import os
import sys
import django
from pathlib import Path

# Setup Django Environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from analyzer.templatetags.custom_filters import clean_markdown
from data_pipeline.parsers.web_scraper import WebScraper
from data_pipeline.autonomous_linker import AutonomousLinker
from analyzer.rag_engine import rag_engine


def test_markdown_cleaner():
    """
    Test that clean_markdown strips raw '###' headers and formats HTML properly.

    :returns: None
    :rtype: None

    :Example:

    >>> test_markdown_cleaner()
    """
    print("[1] Testing Markdown Cleaner Filter...")
    sample_raw = "### Offres chez KCC\n* Postes disponibles à Kolwezi\n**Date** : 2026-08"
    result = clean_markdown(sample_raw)

    assert "###" not in result, "ERROR: Raw '###' still present in output!"
    assert "Offres chez KCC" in result, "ERROR: Header text lost!"
    assert "<strong" in result or "font-extrabold" in result, "ERROR: Bold formatting failed!"
    print("    [✓] Markdown Cleaner Passed! Raw '###' hashes successfully stripped.")


def test_village_afrique_and_web_scraper():
    """
    Test WebScraper logic on Village Afrique and African web targets.

    :returns: None
    :rtype: None

    :Example:

    >>> test_village_afrique_and_web_scraper()
    """
    print("[2] Testing WebScraper on Village Afrique & MediaCongo...")
    scraper = WebScraper()
    
    doc = scraper.scrape_url_content("https://www.villageafrique.com")
    assert "title" in doc and "content" in doc, "ERROR: Invalid document structure!"
    print(f"    [✓] Scraped Village Afrique Title: {doc['title']}")

    doc_mc = scraper.scrape_url_content("https://www.mediacongo.net")
    assert "content" in doc_mc, "ERROR: MediaCongo scraping failed!"
    print(f"    [✓] Scraped MediaCongo Title: {doc_mc['title']}")


def test_autonomous_linker():
    """
    Test AutonomousLinker search and live scraping capabilities.

    :returns: None
    :rtype: None

    :Example:

    >>> test_autonomous_linker()
    """
    print("[3] Testing AutonomousLinker live search & scrape...")
    linker = AutonomousLinker()
    docs = linker.search_and_scrape_web("Village Afrique actualités RDC Kolwezi", max_sites=2)
    assert len(docs) > 0, "ERROR: AutonomousLinker returned 0 documents!"
    print(f"    [✓] AutonomousLinker fetched {len(docs)} live web target documents.")


def test_rag_engine_execution():
    """
    Test RAGEngine query execution and verify response formatting.

    :returns: None
    :rtype: None

    :Example:

    >>> test_rag_engine_execution()
    """
    print("[4] Testing RAGEngine Query Synthesis...")
    res = rag_engine.execute_query("Quelles sont les actualités sur Village Afrique et KCC ?")
    answer = res["answer"]
    
    assert "###" not in answer, "ERROR: RAGEngine response contains raw '###'!"
    print(f"    [✓] RAGEngine Answer snippet:\n{answer[:200]}...")


if __name__ == "__main__":
    print("==================================================")
    print("Running Mayele IA Web Scraper & Cleaner Test Suite")
    print("==================================================")
    test_markdown_cleaner()
    test_village_afrique_and_web_scraper()
    test_autonomous_linker()
    test_rag_engine_execution()
    print("\n[SUCCESS] ALL TESTS PASSED SUCCESSFULLY! 🚀")
