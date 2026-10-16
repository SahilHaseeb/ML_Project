"""
src/collection/base.py
----------------------
Abstract Base Class for all job data collectors.

Collection Principles:
1. Separation: Collection ONLY fetches and archives raw data. It NEVER modifies
   or invents fields.
2. Politeness: Rate limiting, exponential backoff, and timeouts are enforced.
3. Provenance: Every raw batch is archived in `data/raw/` with timestamps and source tags.
"""

from abc import ABC, abstractmethod
import datetime
import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import requests

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """
    Abstract base class for data collectors (APIs, public feeds, or local dumps).
    """

    SOURCE_NAME: str = "base"
    DEFAULT_TIMEOUT_SECONDS: int = 15
    DEFAULT_RATE_LIMIT_SECONDS: float = 2.0

    def __init__(
        self,
        output_dir: str = "data/raw",
        rate_limit: float = DEFAULT_RATE_LIMIT_SECONDS,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Pakistan-AI-Job-Market-Intelligence/2.0 "
                "(Educational Research Project; https://github.com/)"
            )
        })

    def _sleep(self):
        """Respect server limits between calls."""
        if self.rate_limit > 0:
            logger.debug(f"[{self.SOURCE_NAME}] Rate limit sleep: {self.rate_limit}s")
            time.sleep(self.rate_limit)

    @abstractmethod
    def fetch_raw(self, **kwargs) -> Any:
        """
        Fetch raw data from the external source without modifying the payload.
        Must return the native Python structure (e.g. dict or list).
        """
        pass

    @abstractmethod
    def standardize_raw_records(self, raw_data: Any) -> List[Dict[str, Any]]:
        """
        Extract individual job record dictionaries from the raw payload,
        retaining the original raw values before cleaning.
        """
        pass

    def save_raw_json(self, raw_data: Any, suffix: str = "") -> Path:
        """
        Save the unedited raw payload to data/raw/ as JSON for data provenance.
        """
        ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
        tag = f"_{suffix}" if suffix else ""
        filename = f"{self.SOURCE_NAME}_raw_{ts}{tag}.json"
        target_path = self.output_dir / filename

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)

        logger.info(f"[{self.SOURCE_NAME}] Saved raw payload to {target_path}")
        return target_path

    def collect(self, save_raw: bool = True, **kwargs) -> List[Dict[str, Any]]:
        """
        Main collection workflow:
          1. Fetch raw response.
          2. Optionally save raw snapshot to data/raw/.
          3. Extract records and tag with collection metadata.
        """
        logger.info(f"[{self.SOURCE_NAME}] Starting collection...")
        raw_data = self.fetch_raw(**kwargs)
        if not raw_data:
            logger.warning(f"[{self.SOURCE_NAME}] No data returned.")
            return []

        if save_raw:
            self.save_raw_json(raw_data)

        records = self.standardize_raw_records(raw_data)
        logger.info(f"[{self.SOURCE_NAME}] Collected {len(records)} raw job records.")
        return records
