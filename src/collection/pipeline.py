"""
src/collection/pipeline.py
--------------------------
Orchestrates collection across all configured job data sources.

Responsibility:
- Run one or more collectors.
- Archive untouched raw snapshots into data/raw/.
- Return a consolidated raw DataFrame ready for the separate cleaning pipeline.
"""

import datetime
import logging
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from src.collection.api_collectors import (
    RemotiveCollector,
    ArbeitnowCollector,
    LocalRawFileCollector,
)

logger = logging.getLogger(__name__)


class CollectionPipeline:
    """
    Coordinates data collection across multiple public, compliant sources.
    """

    def __init__(self, raw_dir: str = "data/raw"):
        self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        enable_remotive: bool = True,
        enable_arbeitnow: bool = True,
        local_feed_paths: Optional[List[str]] = None,
        remotive_limit: Optional[int] = 25,
        save_consolidated_raw: bool = True,
    ) -> pd.DataFrame:
        """
        Execute collection across enabled sources.
        
        Returns:
            pd.DataFrame: Consolidated raw DataFrame containing raw fields from all sources.
        """
        all_records: List[Dict] = []

        # 1. Remotive Collector
        if enable_remotive:
            logger.info("Executing Remotive API collection...")
            remotive = RemotiveCollector(output_dir=str(self.raw_dir))
            records = remotive.collect(category="software-dev", limit=remotive_limit)
            all_records.extend(records)

        # 2. Arbeitnow Collector
        if enable_arbeitnow:
            logger.info("Executing Arbeitnow API collection...")
            arbeitnow = ArbeitnowCollector(output_dir=str(self.raw_dir))
            records = arbeitnow.collect(page=1)
            all_records.extend(records)

        # 3. Optional Local Feeds (Pakistan local dumps or open datasets)
        if local_feed_paths:
            for feed_path in local_feed_paths:
                logger.info(f"Ingesting local raw feed: {feed_path}")
                local_col = LocalRawFileCollector(feed_path, output_dir=str(self.raw_dir))
                records = local_col.collect(save_raw=False)
                all_records.extend(records)

        raw_df = pd.DataFrame(all_records)
        logger.info(f"Collection complete: aggregated {len(raw_df)} total raw listings.")

        if save_consolidated_raw and not raw_df.empty:
            ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
            raw_csv_path = self.raw_dir / f"aggregated_raw_{ts}.csv"
            raw_df.to_csv(raw_csv_path, index=False)
            logger.info(f"Saved consolidated raw archive: {raw_csv_path}")

        return raw_df
