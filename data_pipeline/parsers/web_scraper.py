"""
X-Ray Universal Web Scraper for African & Global Web Intelligence.

Extracts structured text from HTML portals and PDF documents page-by-page.
Parses top African portals (Village Afrique, MediaCongo, Emploi.cd, Radio Okapi, Zoom Eco),
official government gazettes (Journal Officiel, LEGANET, ANAPI, BCC), and mining corporate sites.

:Example:

>>> from data_pipeline.parsers.web_scraper import WebScraper
>>> scraper = WebScraper()
>>> data = scraper.scrape_url_content("https://www.villageafrique.com")
>>> print(data["title"])
"""

import io
import logging
import random
import re
import urllib.parse
from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup
import pypdf

logger = logging.getLogger(__name__)


class WebScraper:
    """
    Universal High-Performance Web Scraper with PDF page-by-page extraction and deep crawling capabilities.
    """

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    ]

    def __init__(self):
        """
        Initialize WebScraper HTTP Session with browser headers rotation.

        :returns: None
        :rtype: None

        :Example:

        >>> scraper = WebScraper()
        """
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf;q=0.8,*/*;q=0.7",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })

    def _get_soup(self, url: str, timeout: tuple = (5, 15)) -> BeautifulSoup | None:
        """
        Fetch HTML page content with headers rotation and return BeautifulSoup object.

        :param url: Target website URL.
        :type url: str
        :param timeout: Tuple of (connect_timeout, read_timeout) in seconds.
        :type timeout: tuple
        :returns: BeautifulSoup DOM object or None on error.
        :rtype: BeautifulSoup | None

        :Example:

        >>> scraper = WebScraper()
        >>> soup = scraper._get_soup("https://www.villageafrique.com")
        """
        try:
            self.session.headers["User-Agent"] = random.choice(self.USER_AGENTS)
            response = self.session.get(url, timeout=timeout, verify=False)
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
            else:
                logger.warning(f"HTTP Status {response.status_code} for URL: {url}")
        except Exception as exc:
            logger.error(f"Failed HTTP fetch for {url}: {exc}")
        return None

    def scrape_pdf_content(self, url: str) -> List[Dict[str, Any]]:
        """
        Download a PDF file and extract structured text page-by-page.

        Converts every single page of the PDF into a separate text document dictionary
        so all pages are indexed individually in the database and ChromaDB.

        :param url: Direct URL string to the PDF file.
        :type url: str
        :returns: List of document dicts (one per PDF page).
        :rtype: List[Dict[str, Any]]

        :Example:

        >>> scraper = WebScraper()
        >>> pages = scraper.scrape_pdf_content("https://www.bcc.cd/statistiques.pdf")
        >>> print(f"Extracted {len(pages)} PDF pages")
        """
        try:
            self.session.headers["User-Agent"] = random.choice(self.USER_AGENTS)
            response = self.session.get(url, timeout=(5, 25), verify=False)
            if response.status_code == 200:
                pdf_bytes = io.BytesIO(response.content)
                reader = pypdf.PdfReader(pdf_bytes)
                num_pages = len(reader.pages)
                pdf_name = url.split("/")[-1].split("?")[0] or "Document PDF"

                page_docs = []
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    page_text = page.extract_text() or ""
                    cleaned_text = " ".join(page_text.split())
                    if len(cleaned_text) > 30:
                        page_docs.append({
                            "title": f"{pdf_name} — Page {page_num + 1}/{num_pages}",
                            "content": cleaned_text,
                            "url": f"{url}#page={page_num + 1}",
                            "source_type": "gazette" if any(k in url.lower() for k in ["journal", "jo", "decret", "loi", "bcc"]) else "news",
                            "confidence_score": 0.98,
                        })
                if page_docs:
                    logger.info(f"[PDF Extracted] {url} → {len(page_docs)} pages extracted")
                    return page_docs
        except Exception as exc:
            logger.warning(f"Failed PDF extraction for {url}: {exc}")

        return [{
            "title": f"PDF Inaccessible : {url[:60]}",
            "content": "",
            "url": url,
            "source_type": "news",
            "confidence_score": 0.0,
        }]

    def extract_sublinks(self, url: str, soup: BeautifulSoup, max_links: int = 5) -> List[str]:
        """
        Extract internal article, document, and PDF links from an HTML page for deep crawling.

        :param url: Source URL.
        :type url: str
        :param soup: BeautifulSoup DOM object.
        :type soup: BeautifulSoup
        :param max_links: Maximum number of links to extract.
        :type max_links: int
        :returns: List of absolute URL strings.
        :rtype: List[str]

        :Example:

        >>> scraper = WebScraper()
        >>> soup = scraper._get_soup("https://zoom-eco.net")
        >>> links = scraper.extract_sublinks("https://zoom-eco.net", soup)
        """
        sublinks = []
        base_domain = urllib.parse.urlparse(url).netloc

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            full_url = urllib.parse.urljoin(url, href)
            parsed = urllib.parse.urlparse(full_url)

            # Accept PDFs or internal HTML subpages
            if parsed.netloc == base_domain:
                if full_url.endswith(".pdf") or any(kw in full_url.lower() for kw in ["/article/", "/actu/", "/economie/", "/mines/", "/offre/", "/decret/"]):
                    if full_url not in sublinks and full_url != url:
                        sublinks.append(full_url)
                        if len(sublinks) >= max_links:
                            break

        return sublinks

    def scrape_village_afrique(self, url: str) -> Dict[str, Any]:
        """
        Scrape specialized news, business, and job announcements from Village Afrique.

        :param url: Village Afrique URL.
        :type url: str
        :returns: Dict containing scraped content and metadata.
        :rtype: Dict[str, Any]
        """
        soup = self._get_soup(url)
        if soup:
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            title = soup.title.string.strip() if soup.title else "Village Afrique Portal"
            text = " ".join(soup.get_text(separator=" ").split())
            if len(text) > 100:
                return {
                    "title": title,
                    "content": text[:5000],
                    "url": url,
                    "source_type": "news",
                    "confidence_score": 0.98,
                }

        return {
            "title": "Village Afrique - Source Inaccessible",
            "content": "",
            "url": url,
            "source_type": "news",
            "confidence_score": 0.0,
        }

    def scrape_mediacongo(self, url: str) -> Dict[str, Any]:
        """
        Scrape specialized job tenders and news from MediaCongo RDC.

        :param url: MediaCongo URL.
        :type url: str
        :returns: Dict containing scraped content and metadata.
        :rtype: Dict[str, Any]
        """
        soup = self._get_soup(url)
        if soup:
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            title = soup.title.string.strip() if soup.title else "MediaCongo RDC"
            text = " ".join(soup.get_text(separator=" ").split())
            if len(text) > 100:
                return {
                    "title": title,
                    "content": text[:5000],
                    "url": url,
                    "source_type": "mining_tender" if any(w in url for w in ["emploi", "offre", "job"]) else "news",
                    "confidence_score": 0.97,
                }

        return {
            "title": "MediaCongo RDC - Source Inaccessible",
            "content": "",
            "url": url,
            "source_type": "news",
            "confidence_score": 0.0,
        }

    def scrape_url_content(self, url: str) -> Dict[str, Any] | List[Dict[str, Any]]:
        """
        Universal scraper endpoint to extract text content from ANY URL (HTML or PDF).

        If the target is a PDF file, extracts and returns a list of individual page documents.
        If HTML, extracts article text and returns a single document dict.

        :param url: Target web URL string.
        :type url: str
        :returns: Single document dict OR list of PDF page document dicts.
        :rtype: Dict[str, Any] | List[Dict[str, Any]]

        :Example:

        >>> scraper = WebScraper()
        >>> res = scraper.scrape_url_content("https://journalofficiel.cd")
        """
        url_lower = url.lower()

        # PDF files processing (page-by-page text extraction)
        if url_lower.endswith(".pdf") or ".pdf?" in url_lower:
            return self.scrape_pdf_content(url)

        # Domain routing
        if "villageafrique" in url_lower or "village-afrique" in url_lower:
            return self.scrape_village_afrique(url)
        elif "mediacongo" in url_lower:
            return self.scrape_mediacongo(url)

        # Universal HTML extraction
        soup = self._get_soup(url)
        if soup:
            for tag in soup(["script", "style", "nav", "footer", "header", "iframe"]):
                tag.decompose()

            title = soup.title.string.strip() if soup.title else f"Content from {url}"

            main_element = (
                soup.find("article") or
                soup.find("main") or
                soup.find("div", class_=re.compile(r"content|body|main|post", re.I)) or
                soup.body
            )

            raw_text = " ".join(main_element.get_text(separator=" ").split()) if main_element else ""

            if len(raw_text) > 100:
                source_type = "news"
                if any(k in url_lower for k in ["job", "career", "recrutement", "offre", "onem"]):
                    source_type = "mining_tender"
                elif any(k in url_lower for k in ["journal", "officiel", "decret", "loi"]):
                    source_type = "gazette"

                return {
                    "title": title,
                    "content": raw_text[:5000],
                    "url": url,
                    "source_type": source_type,
                    "confidence_score": 0.96,
                }

        # Failed fetch fallback
        return {
            "title": f"Source inaccessible : {url[:60]}",
            "content": "",
            "url": url,
            "source_type": "news",
            "confidence_score": 0.0,
        }

    def scrape_batch(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape a batch list of target web URLs sequentially, flattening PDF page documents into the result list.

        :param urls: List of target URL strings.
        :type urls: List[str]
        :returns: List of scraped document dictionaries.
        :rtype: List[Dict[str, Any]]

        :Example:

        >>> scraper = WebScraper()
        >>> docs = scraper.scrape_batch(["https://www.villageafrique.com", "https://www.mediacongo.net"])
        """
        results = []
        for u in urls:
            try:
                res = self.scrape_url_content(u)
                if isinstance(res, list):
                    results.extend(res)
                elif res and res.get("content"):
                    results.append(res)
            except Exception as exc:
                logger.error(f"Error scraping batch item {u}: {exc}")
        return results
