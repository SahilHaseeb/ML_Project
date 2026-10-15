"""
src/scraping/base_scraper.py
------------------------------
Abstract base class for all data source scrapers.

Every real scraper (e.g., RozeeScraper) will inherit from this class
and implement the three abstract methods: fetch(), parse(), save().

By enforcing this interface we make it easy to:
- Add new sources without changing the rest of the code.
- Test each scraper independently.
- Swap sources in or out without breaking the pipeline.

⚠️  NO real scraping is implemented in Phase 1.
    This is the architecture skeleton only.
"""

import abc
import logging
import time
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

# Minimum delay between HTTP requests (seconds) — be polite to servers
DEFAULT_RATE_LIMIT_SECONDS = 2.0


class BaseScraper(abc.ABC):
    """
    Abstract base class that all source-specific scrapers must inherit.

    Subclasses must implement:
        - fetch(url)   → raw HTTP response or soup object
        - parse(raw)   → list of job dicts
        - get_urls()   → list of URLs to scrape

    The `run()` method orchestrates the full scrape and calls save().
    """

    SOURCE_NAME: str = "unknown"    # Override in each subclass
    BASE_URL: str = ""              # Override in each subclass
    ROBOTS_TXT_CHECKED: bool = False  # Must be set True after checking

    def __init__(self, output_dir: str = "data/raw", rate_limit: float = DEFAULT_RATE_LIMIT_SECONDS):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limit = rate_limit
        self._jobs: list[dict] = []

    @abc.abstractmethod
    def fetch(self, url: str):
        """
        Fetch raw content from `url`.
        Return whatever form (HTML text, JSON dict) your parser expects.
        Must respect rate limits and robots.txt.
        """

    @abc.abstractmethod
    def parse(self, raw) -> list[dict]:
        """
        Parse the raw content into a list of job dictionaries.
        Each dict should match the job data schema in docs/data_schema.md.
        Missing fields should be set to None — never invented.
        """

    @abc.abstractmethod
    def get_urls(self) -> list[str]:
        """Return the list of page URLs this scraper should visit."""

    def _rate_limit_sleep(self):
        """Sleep between requests to avoid overwhelming a server."""
        logger.debug(f"Rate limiting: sleeping {self.rate_limit}s")
        time.sleep(self.rate_limit)

    def run(self) -> pd.DataFrame:
        """
        Orchestrate the full scrape:
        1. Get URLs
        2. For each URL: fetch → parse → accumulate
        3. Return as DataFrame

        Does NOT save automatically — call save() if you want persistence.
        """
        urls = self.get_urls()
        logger.info(f"[{self.SOURCE_NAME}] Scraping {len(urls)} URL(s) …")

        for url in urls:
            try:
                raw = self.fetch(url)
                jobs = self.parse(raw)
                self._jobs.extend(jobs)
                logger.info(f"  Parsed {len(jobs)} jobs from {url}")
            except Exception as e:
                logger.error(f"  Error scraping {url}: {e}")
            self._rate_limit_sleep()

        logger.info(f"[{self.SOURCE_NAME}] Total jobs collected: {len(self._jobs)}")
        return pd.DataFrame(self._jobs)

    def save(self, df: pd.DataFrame, filename: str | None = None) -> Path:
        """
        Save the scraped DataFrame to a CSV file in output_dir.
        The filename defaults to  <source_name>_raw_<timestamp>.csv
        """
        import datetime
        ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        fname = filename or f"{self.SOURCE_NAME}_raw_{ts}.csv"
        out_path = self.output_dir / fname
        df.to_csv(out_path, index=False)
        logger.info(f"Saved {len(df)} rows → {out_path}")
        return out_path
