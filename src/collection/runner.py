"""
src/collection/runner.py
------------------------
CLI entry point to execute job data collection and data cleaning.

Usage:
    python src/collection/runner.py
    python src/collection/runner.py --limit 20
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.collection.pipeline import CollectionPipeline
from src.data_processing.cleaner import clean_pipeline, save_cleaned_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("collection_runner")


def main():
    parser = argparse.ArgumentParser(description="Pakistan AI Job Market Intelligence - Collection Runner")
    parser.add_argument("--limit", type=int, default=25, help="Limit number of jobs to fetch per API")
    parser.add_argument("--skip-remotive", action="store_true", help="Skip Remotive API")
    parser.add_argument("--skip-arbeitnow", action="store_true", help="Skip Arbeitnow API")
    parser.add_argument("--no-clean", action="store_true", help="Only collect raw data; skip cleaning")
    args = parser.parse_args()

    logger.info("Initializing collection pipeline...")
    pipeline = CollectionPipeline(raw_dir="data/raw")

    raw_df = pipeline.run(
        enable_remotive=not args.skip_remotive,
        enable_arbeitnow=not args.skip_arbeitnow,
        remotive_limit=args.limit,
    )

    if raw_df.empty:
        logger.warning("No listings collected. Exiting.")
        return

    logger.info(f"Successfully collected {len(raw_df)} raw listings.")

    if not args.no_clean:
        logger.info("Running cleaning pipeline on collected raw data...")
        clean_df, report = clean_pipeline(raw_df)
        out_path = save_cleaned_data(clean_df, output_path="data/processed/cleaned_jobs.csv")
        logger.info(f"Cleaned {len(clean_df)} jobs saved to: {out_path}")
        logger.info(f"Geographic Scope Breakdown:\n{clean_df['location_scope'].value_counts()}")


if __name__ == "__main__":
    main()
