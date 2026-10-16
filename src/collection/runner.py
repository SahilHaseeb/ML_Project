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
from src.data_processing.cleaner import (
    clean_pipeline,
    save_cleaned_data,
    safe_incremental_save,
    load_cleaned_data,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("collection_runner")


def run_collection(
    limit: int = 25,
    skip_remotive: bool = False,
    skip_arbeitnow: bool = False,
    no_clean: bool = False,
    merge_existing: bool = True,
    output_path: str = "data/processed/cleaned_jobs.csv",
    raw_dir: str = "data/raw",
) -> dict:
    """
    Executes the job collection and data cleaning pipeline with safe incremental merging.

    Guarantees:
    - If APIs fail or return 0 listings, existing cleaned_jobs.csv is NEVER overwritten or corrupted.
    - If merge_existing=True, newly collected jobs are merged with existing records and deduplicated.
    """
    logger.info("Initializing collection pipeline...")
    pipeline = CollectionPipeline(raw_dir=raw_dir)

    try:
        raw_df = pipeline.run(
            enable_remotive=not skip_remotive,
            enable_arbeitnow=not skip_arbeitnow,
            remotive_limit=limit,
        )
    except Exception as e:
        logger.error(f"Collection pipeline encountered unexpected error: {e}")
        raw_df = None

    # Handle empty or failed collection safely
    if raw_df is None or raw_df.empty:
        existing_df = load_cleaned_data(output_path)
        existing_count = len(existing_df) if existing_df is not None else 0
        if existing_count > 0:
            logger.warning(
                f"No new listings collected from APIs. Existing cleaned dataset "
                f"({existing_count} rows) at {output_path} is safely preserved."
            )
            return {"status": "preserved", "total_jobs": existing_count, "added": 0, "output_path": output_path}
        else:
            logger.warning("No listings collected and no existing dataset found.")
            return {"status": "empty", "total_jobs": 0, "added": 0, "output_path": output_path}

    logger.info(f"Successfully collected {len(raw_df)} raw listings.")

    if no_clean:
        return {"status": "raw_only", "raw_count": len(raw_df)}

    logger.info("Running cleaning pipeline on collected raw data...")
    clean_df, report = clean_pipeline(raw_df)

    if merge_existing:
        out_path, total_rows, added_rows = safe_incremental_save(clean_df, output_path=output_path)
    else:
        out_path = save_cleaned_data(clean_df, output_path=output_path)
        total_rows = len(clean_df)
        added_rows = len(clean_df)

    logger.info(f"Cleaned dataset: {total_rows} total jobs ({added_rows} new) saved to: {out_path}")
    if "location_scope" in clean_df.columns:
        logger.info(f"Geographic Scope Breakdown:\n{clean_df['location_scope'].value_counts()}")

    return {
        "status": "success",
        "total_jobs": total_rows,
        "added": added_rows,
        "output_path": str(out_path),
        "quality_report": report,
    }


def main():
    parser = argparse.ArgumentParser(description="Pakistan AI Job Market Intelligence - Collection Runner")
    parser.add_argument("--limit", type=int, default=25, help="Limit number of jobs to fetch per API")
    parser.add_argument("--skip-remotive", action="store_true", help="Skip Remotive API")
    parser.add_argument("--skip-arbeitnow", action="store_true", help="Skip Arbeitnow API")
    parser.add_argument("--no-clean", action="store_true", help="Only collect raw data; skip cleaning")
    parser.add_argument("--no-merge", action="store_true", help="Overwrite instead of merging with existing cleaned dataset")
    parser.add_argument("--output-path", type=str, default="data/processed/cleaned_jobs.csv", help="Target cleaned CSV path")
    parser.add_argument("--raw-dir", type=str, default="data/raw", help="Target raw archive directory")
    args = parser.parse_args()

    result = run_collection(
        limit=args.limit,
        skip_remotive=args.skip_remotive,
        skip_arbeitnow=args.skip_arbeitnow,
        no_clean=args.no_clean,
        merge_existing=not args.no_merge,
        output_path=args.output_path,
        raw_dir=args.raw_dir,
    )
    logger.info(f"Runner completed with result: {result}")


if __name__ == "__main__":
    main()
