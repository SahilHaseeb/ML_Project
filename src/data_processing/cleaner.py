"""
src/data_processing/cleaner.py
--------------------------------
The main cleaning pipeline.

It ties together validators and normalizers in the correct order:
  1. Validate required columns
  2. Normalize city / category / skills
  3. Parse and validate dates
  4. Validate numeric ranges
  5. Deduplicate rows
  6. Return the clean DataFrame + a quality report

Think of this module as an assembly line: raw data goes in, clean data
comes out, and every step is logged so you can trace problems.
"""

import hashlib
import logging
import pandas as pd

from src.data_processing.validators import (
    validate_required_columns,
    validate_schema,
    validate_date_column,
    validate_numeric_range,
    generate_quality_report,
)
from src.data_processing.normalizers import (
    normalize_location_column,
    normalize_category_column,
    normalize_skills_column,
)

logger = logging.getLogger(__name__)


def _compute_job_hash(row: pd.Series) -> str:
    """
    Create a fingerprint for a job listing based on its key fields.
    
    We use: title + company + posting_date (lowercased and stripped).
    If two rows share the same fingerprint they are likely duplicates.
    
    Why MD5? It is fast and sufficient for deduplication — we are not
    doing cryptographic security here.
    """
    parts = [
        str(row.get("title", "")).strip().lower(),
        str(row.get("company", "")).strip().lower(),
        str(row.get("posting_date", "")).strip(),
    ]
    raw = "|".join(parts)
    return hashlib.md5(raw.encode()).hexdigest()


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate job listings.
    
    Strategy:
    - Compute a hash for each row.
    - Keep only the first occurrence of each hash.
    - Log how many duplicates were removed.
    """
    before = len(df)
    df = df.copy()
    df["_hash"] = df.apply(_compute_job_hash, axis=1)
    df = df.drop_duplicates(subset="_hash", keep="first")
    df = df.drop(columns=["_hash"])
    removed = before - len(df)
    if removed > 0:
        logger.info(f"Deduplication: removed {removed} duplicate row(s).")
    return df.reset_index(drop=True)


def clean_pipeline(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Run the full cleaning pipeline on a raw DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Raw job data — could come from CSV, scraper, or DB.

    Returns
    -------
    clean_df : pd.DataFrame
        Cleaned and normalized data.
    report : dict
        A data-quality report showing completeness per column.
    """
    logger.info(f"Starting clean pipeline on {len(df)} row(s).")

    # ── Step 1: Validate required columns ─────────────────────────────────────
    is_valid, missing = validate_required_columns(df)
    if not is_valid:
        raise ValueError(
            f"Data is missing required columns: {missing}. "
            f"Cannot continue cleaning."
        )

    # Log any optional columns that are absent
    validate_schema(df)

    # ── Step 2: Work on a copy (never mutate the original) ────────────────────
    df = df.copy()

    # ── Step 3: Normalize free-text columns ───────────────────────────────────
    df = normalize_location_column(df)
    df = normalize_category_column(df)
    df = normalize_skills_column(df)

    # ── Step 4: Parse and validate dates ──────────────────────────────────────
    df = validate_date_column(df, "posting_date")
    df = validate_date_column(df, "scraped_at")

    # ── Step 5: Validate numeric ranges ───────────────────────────────────────
    df = validate_numeric_range(df, "salary_min", "salary_max")
    df = validate_numeric_range(df, "experience_min", "experience_max")

    # ── Step 6: Strip leading/trailing whitespace from text columns ───────────
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(
        lambda col: col.str.strip() if col.dtype == "object" else col
    )

    # ── Step 7: Deduplicate ───────────────────────────────────────────────────
    df = deduplicate(df)

    # ── Step 8: Generate quality report ───────────────────────────────────────
    report = generate_quality_report(df)

    logger.info(
        f"Clean pipeline complete. Output: {len(df)} row(s). "
        f"Total rows (including NaN): {report['total_rows']}"
    )

    return df, report


def load_sample_data(path: str = "data/sample/sample_jobs.csv") -> pd.DataFrame:
    """
    Convenience function: load the sample CSV and run the clean pipeline.
    Returns the clean DataFrame.
    """
    df = pd.read_csv(path, low_memory=False)
    clean_df, report = clean_pipeline(df)
    return clean_df
