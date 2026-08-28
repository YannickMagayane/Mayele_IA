"""
Autonomous Linker — Direct URL Scraping Engine for RDC & African Web.

Scrapes all 50+ registered target websites directly and concurrently (ThreadPool)
without depending on Google CSE API. Uses keyword-based routing to target the most
relevant portal for each query.

:Example:

>>> from data_pipeline.autonomous_linker import AutonomousLinker
>>> linker = AutonomousLinker()
>>> docs = linker.search_and_scrape_web("actualités économiques RDC", max_sites=4)
>>> print(docs[0]["title"])
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from data_pipeline.parsers.web_scraper import WebScraper

logger = logging.getLogger(__name__)


class AutonomousLinker:
    """
    Direct web scraping engine for RDC & African portals.

    Queries target sites in parallel using ThreadPoolExecutor for maximum throughput.
    No external API dependency — all target URLs are registered directly.
    """

    # ==========================================================================
    # ALL TARGET WEBSITES — 50+ portals covering DRC institutions,
    # mining, media, finance, security, and academic sources
    # =========================================================================
    DIRECT_TARGET_URLS = [
        # === Médias Nationaux & Africains (haute disponibilité réseau) ===
        "https://www.jeuneafrique.com",
        "https://www.radiookapi.net/economie",
        "https://zoom-eco.net",
        "https://7sur7.cd",
        "https://www.politico.cd",
        "https://www.thebulletin.be",
        "https://actualite.cd",
        "https://actu7.cd",
        "https://www.mediacongo.net",
        "https://www.digitalcongo.net",
        "https://topcongo.live",
        "https://www.rtnc.cd",
        "https://deskeco.com",
        "https://congoindependant.com",
        "https://yabisonews.com",
        "https://acpcongo.com",

        # === Village Afrique ===
        "https://www.villageafrique.com",
        "https://village-afrique.com",

        # === Mining & Corporate ===
        "https://www.glencore.com/careers",
        "https://www.glencore.cd/fr/vacancies",
        "https://www.ivanhoemines.com/careers",
        "https://ivanhoemines.simplify.hr",
        "https://www.mmg.com/careers",

        # === Institutions RDC Officielles ===
        "https://www.onem.cd",
        "https://www.anapi.org",
        "https://www.mines-rdc.cd",
        "https://www.arsp.cd",
        "https://www.bcc.cd",
        "https://www.justice.gouv.cd",
        "https://www.leganet.cd",
        "https://fogec.cd",
        "https://guce.cd",
        "https://www.dgi.gouv.cd",
        "https://www.dgda.cd",
        "https://www.drad.cd",

        # === Sécurité & Gouvernance ===
        "https://kivusecurity.org",
        "https://fec-rdc.com",

        # === Finance & Banques ===
        "https://www.tmb.cd",
        "https://www.rawbank.com",
        "https://www.equitygroupholdings.com",

        # === Académique & Archives ===
        "https://arxiv.org",
        "https://openlibrary.org",
        "https://africaresearchonline.com",
    ]

    # Keyword → preferred URL routing for direct query targeting
    KEYWORD_URL_ROUTING = {
        "emploi": ["https://www.onem.cd", "https://www.mediacongo.net"],
        "recrutement": ["https://www.mediacongo.net", "https://actualite.cd"],
        "mine": ["https://zoom-eco.net", "https://www.mines-rdc.cd"],
        "minier": ["https://zoom-eco.net", "https://www.arsp.cd"],
        "glencore": ["https://www.glencore.com/careers", "https://www.glencore.cd/fr/vacancies"],
        "ivanhoe": ["https://www.ivanhoemines.com/careers", "https://ivanhoemines.simplify.hr"],
        "mmg": ["https://www.mmg.com/careers"],
        "actualit": ["https://www.radiookapi.net/economie", "https://7sur7.cd", "https://actualite.cd"],
        "economi": ["https://zoom-eco.net", "https://deskeco.com"],
        "village": ["https://www.villageafrique.com", "https://village-afrique.com"],
        "mediacongo": ["https://www.mediacongo.net"],
        "lualaba": ["https://zoom-eco.net", "https://www.mines-rdc.cd"],
        "kivu": ["https://kivusecurity.org", "https://www.radiookapi.net/economie"],
        "finance": ["https://www.bcc.cd", "https://deskeco.com"],
        "afrique": ["https://www.jeuneafrique.com", "https://www.radiookapi.net/economie"],
        "politique": ["https://www.politico.cd", "https://actualite.cd"],
        "justice": ["https://www.justice.gouv.cd"],
        "anapi": ["https://www.anapi.org"],
        "arsp": ["https://www.arsp.cd"],
        "invest": ["https://www.anapi.org", "https://zoom-eco.net"],
        "kinshasa": ["https://actualite.cd", "https://7sur7.cd"],
        "lubumbashi": ["https://zoom-eco.net", "https://deskeco.com"],
        "kolwezi": ["https://zoom-eco.net", "https://www.mines-rdc.cd"],
        "banque": ["https://www.bcc.cd", "https://www.tmb.cd"],
        "decret": ["https://www.leganet.cd", "https://www.justice.gouv.cd"],
        "offre": ["https://www.mediacongo.net", "https://www.onem.cd"],
        "securite": ["https://kivusecurity.org"],
    }

    def __init__(self):
        """
        Initialize the AutonomousLinker with a WebScraper instance.

        :returns: None
        :rtype: None

        :Example:

        >>> linker = AutonomousLinker()
        """
        self.scraper = WebScraper()
        logger.info(f"[AutonomousLinker] Ready — {len(self.DIRECT_TARGET_URLS)} registered targets, no external API dependency.")

    def _resolve_targets(self, query: str, max_sites: int) -> list:
        """
        Resolve the best target URLs for a given query using keyword routing.

        :param query: User query string.
        :type query: str
        :param max_sites: Maximum number of URLs to resolve.
        :type max_sites: int
        :returns: List of target URL strings.
        :rtype: list

        :Example:

        >>> linker = AutonomousLinker()
        >>> urls = linker._resolve_targets("emploi mines RDC", max_sites=3)
        """
        q_lower = query.lower()
        matched = []
        seen = set()

        for keyword, urls in self.KEYWORD_URL_ROUTING.items():
            if keyword in q_lower:
                for u in urls:
                    if u not in seen:
                        seen.add(u)
                        matched.append(u)

        # If no keyword match, use top reliable directly accessible targets
        if not matched:
            matched = [u for u in self.DIRECT_TARGET_URLS if u not in seen]

        return matched[:max_sites + 2]

    def _scrape_single(self, url: str) -> list[dict]:
        """
        Scrape a single URL or PDF document and return a list of extracted document dicts.

        :param url: Target URL string (HTML or PDF).
        :type url: str
        :returns: List of extracted document dicts (one or more per PDF page).
        :rtype: list[dict]

        :Example:

        >>> linker = AutonomousLinker()
        >>> docs = linker._scrape_single("https://zoom-eco.net")
        """
        try:
            res = self.scraper.scrape_url_content(url)
            if isinstance(res, list):
                return [d for d in res if d.get("content") and len(d["content"]) > 30]
            elif isinstance(res, dict) and res.get("content") and len(res["content"]) > 50 and res.get("confidence_score", 0) > 0:
                return [res]
        except Exception as exc:
            logger.warning(f"[Scrape] Error for {url}: {exc}")
        return []

    def search_and_scrape_web(self, query: str, max_sites: int = 3) -> list:
        """
        Resolve target URLs by keyword routing and scrape them concurrently via ThreadPool.

        Filters out any failed/empty results — never returns hallucinated content.

        :param query: Natural language search query string.
        :type query: str
        :param max_sites: Maximum number of real content documents to return.
        :type max_sites: int
        :returns: List of scraped documents with real content.
        :rtype: list

        :Example:

        >>> linker = AutonomousLinker()
        >>> docs = linker.search_and_scrape_web("emploi recrutement RDC", max_sites=3)
        >>> print(len(docs), "documents collected")
        """
        targets = self._resolve_targets(query, max_sites)
        collected = []

        logger.info(f"[Scrape] '{query}' → trying {len(targets)} targets concurrently")

        with ThreadPoolExecutor(max_workers=min(len(targets), 6)) as pool:
            futures = {pool.submit(self._scrape_single, url): url for url in targets}
            for future in as_completed(futures, timeout=20):
                url = futures[future]
                try:
                    docs = future.result()
                    if docs:
                        collected.extend(docs)
                        logger.info(f"[Scrape] ✅ {url[:50]} → {len(docs)} document(s) extracted")
                        if len(collected) >= max_sites:
                            break
                except Exception as exc:
                    logger.warning(f"[Scrape] ❌ {url}: {exc}")

        logger.info(f"[Scrape] Done: {len(collected)}/{max_sites} real documents collected for '{query}'")
        return collected[:max_sites]

    def discover_all(self) -> list:
        """
        Scrape ALL registered target URLs and PDF documents concurrently and return results.

        Used by the scheduled background ingestion pipeline (runs at 00:00 and 12:00).

        :returns: List of successfully scraped document dicts.
        :rtype: list

        :Example:

        >>> linker = AutonomousLinker()
        >>> docs = linker.discover_all()
        >>> print(f"{len(docs)} documents ingested")
        """
        collected = []
        logger.info(f"[DiscoverAll] Starting full scrape of {len(self.DIRECT_TARGET_URLS)} registered targets")

        with ThreadPoolExecutor(max_workers=12) as pool:
            futures = {pool.submit(self._scrape_single, url): url for url in self.DIRECT_TARGET_URLS}
            try:
                for future in as_completed(futures, timeout=45):
                    url = futures[future]
                    try:
                        docs = future.result()
                        if docs:
                            collected.extend(docs)
                            logger.info(f"[DiscoverAll] ✅ {url[:50]} → {len(docs)} document(s) extracted")
                    except Exception as exc:
                        logger.warning(f"[DiscoverAll] ❌ {url}: {exc}")
            except TimeoutError:
                logger.info(f"[DiscoverAll] Timeout reached (45s). Returning {len(collected)} collected documents.")

        logger.info(f"[DiscoverAll] Complete: {len(collected)} document(s) scraped from {len(self.DIRECT_TARGET_URLS)} targets")

        return collected

