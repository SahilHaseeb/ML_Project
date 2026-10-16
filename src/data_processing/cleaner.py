"""
src/data_processing/cleaner.py
--------------------------------
The main cleaning and standardization pipeline.

Pipeline Stages:
  1. Detect raw collection columns and standardize into canonical schema.
  2. Normalize job titles and clean company names.
  3. Classify geographic location scope (Pakistan on-site vs worldwide remote).
  4. Normalize city, category, and skills.
  5. Parse and validate dates.
  6. Safely parse salary and experience ranges when available (never invent).
  7. Validate numeric ranges (min <= max).
  8. Deduplicate listings using URL or multi-field fingerprinting.
  9. Generate data quality completeness report.
"""

import hashlib
import logging
import os
from pathlib import Path
from typing import Optional, Tuple
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
    classify_location_scope,
    clean_job_title,
    clean_company_name,
    parse_experience_years,
    parse_salary,
    infer_category,
)

logger = logging.getLogger(__name__)


def _compute_job_hash(row: pd.Series) -> str:
    """
    Create a fingerprint for a job listing based on its key fields.
    Prioritizes URL if present; otherwise uses title + company + location + date.
    """
    url = str(row.get("job_url", "")).strip()
    if url and url.lower() not in ["none", "nan", ""]:
        return hashlib.md5(url.lower().encode("utf-8")).hexdigest()

    parts = [
        str(row.get("title", "")).strip().lower(),
        str(row.get("company", "")).strip().lower(),
        str(row.get("location", "")).strip().lower(),
        str(row.get("posting_date", "")).strip(),
    ]
    raw = "|".join(parts)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate job listings based on fingerprint hash.
    Keeps the first occurrence of each unique listing.
    """
    if df.empty:
        return df
    before = len(df)
    df = df.copy()
    df["_hash"] = df.apply(_compute_job_hash, axis=1)
    df = df.drop_duplicates(subset="_hash", keep="first")
    df = df.drop(columns=["_hash"])
    removed = before - len(df)
    if removed > 0:
        logger.info(f"Deduplication: removed {removed} duplicate row(s).")
    return df.reset_index(drop=True)


def standardize_raw_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms raw collector payloads into the canonical schema.
    Safely parses fields and leaves missing values as None/NaN.
    """
    rows = []
    for idx, r in raw_df.iterrows():
        title_raw = str(r.get("title_raw") or r.get("title") or "").strip()
        comp_raw = str(r.get("company_raw") or r.get("company") or "").strip()
        loc_raw = str(r.get("location_raw") or r.get("location") or "").strip()
        cand_loc_raw = str(r.get("candidate_location_raw") or "").strip()
        sal_raw = str(r.get("salary_raw") or r.get("salary") or "").strip()
        skills_raw = str(r.get("skills_raw") or r.get("skills") or "").strip()
        desc_raw = str(r.get("description_raw") or r.get("description") or "").strip()
        date_raw = str(r.get("posting_date_raw") or r.get("posting_date") or "").strip()
        src = str(r.get("source") or "unknown").strip()
        url = str(r.get("job_url") or "").strip()
        scraped_at = str(r.get("collected_at") or r.get("scraped_at") or "").strip()

        # Generate or preserve job_id
        job_id = str(r.get("raw_job_id") or r.get("job_id") or f"COL-{idx+1:04d}")

        # Clean fields
        clean_title = clean_job_title(title_raw)
        clean_company = clean_company_name(comp_raw) if comp_raw else None
        loc_scope = classify_location_scope(loc_raw, cand_loc_raw)

        # Parse salary safely
        sal_min, sal_max, currency = parse_salary(sal_raw)

        # Parse experience safely from description or title
        exp_min, exp_max = parse_experience_years(f"{title_raw} {desc_raw[:300]}")

        # Category
        cat_raw = r.get("category_raw") or r.get("category")
        category = str(cat_raw).strip() if cat_raw and str(cat_raw).lower() not in ["none", "nan", ""] else infer_category(clean_title, skills_raw)

        rows.append({
            "job_id": job_id,
            "title": clean_title,
            "company": clean_company,
            "location": loc_raw if loc_raw else None,
            "candidate_location": cand_loc_raw if cand_loc_raw else None,
            "location_scope": loc_scope,
            "category": category,
            "salary_min": sal_min,
            "salary_max": sal_max,
            "salary_currency": currency,
            "experience_min": exp_min,
            "experience_max": exp_max,
            "education": r.get("education") if pd.notna(r.get("education")) else None,
            "job_type": r.get("job_type_raw") or r.get("job_type") or None,
            "skills": skills_raw if skills_raw else None,
            "description": desc_raw if desc_raw else None,
            "posting_date": date_raw if date_raw else None,
            "source": src,
            "job_url": url if url else None,
            "scraped_at": scraped_at if scraped_at else None,
        })

    return pd.DataFrame(rows)


def clean_pipeline(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """
    Run the full cleaning pipeline on a raw or canonical DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Raw or partially standardized job data.

    Returns
    -------
    clean_df : pd.DataFrame
        Cleaned and normalized data with location scopes.
    report : dict
        A data-quality report showing completeness per column.
    """
    if df.empty:
        return df, {"total_rows": 0, "missing_values": {}, "completeness_pct": {}}

    logger.info(f"Starting clean pipeline on {len(df)} row(s).")
    df = df.copy()

    # ── Step 1: Detect raw collector columns and map to schema ────────────────
    if "title_raw" in df.columns or "raw_job_id" in df.columns:
        df = standardize_raw_dataframe(df)

    # Ensure required columns
    is_valid, missing = validate_required_columns(df)
    if not is_valid:
        raise ValueError(f"Data is missing required columns: {missing}. Cannot continue cleaning.")

    # ── Step 2: Clean titles and companies ────────────────────────────────────
    if "title" in df.columns:
        df["title"] = df["title"].apply(lambda t: clean_job_title(t) if isinstance(t, str) else t)
    if "company" in df.columns:
        df["company"] = df["company"].apply(lambda c: clean_company_name(c) if isinstance(c, str) else c)

    # ── Step 3: Classify location scope if not already done ───────────────────
    if "location_scope" not in df.columns:
        cand_loc_col = "candidate_location" if "candidate_location" in df.columns else "location"
        df["location_scope"] = df.apply(
            lambda r: classify_location_scope(str(r.get("location", "")), str(r.get(cand_loc_col, ""))),
            axis=1,
        )

    # ── Step 4: Normalize city, category, and skills ──────────────────────────
    df = normalize_location_column(df)
    df = normalize_category_column(df)
    df = normalize_skills_column(df)

    # ── Step 5: Parse and validate dates ──────────────────────────────────────
    df = validate_date_column(df, "posting_date")
    df = validate_date_column(df, "scraped_at")

    # ── Step 6: Validate numeric ranges ───────────────────────────────────────
    df = validate_numeric_range(df, "salary_min", "salary_max")
    df = validate_numeric_range(df, "experience_min", "experience_max")

    # ── Step 7: Strip leading/trailing whitespace from text columns ───────────
    str_cols = df.select_dtypes(include=["object", "string"]).columns
    df[str_cols] = df[str_cols].apply(
        lambda col: col.str.strip() if hasattr(col, "str") else col
    )

    # ── Step 8: Deduplicate ───────────────────────────────────────────────────
    df = deduplicate(df)

    # ── Step 9: Generate quality report ───────────────────────────────────────
    report = generate_quality_report(df)

    logger.info(
        f"Clean pipeline complete. Output: {len(df)} row(s). "
        f"Total rows: {report['total_rows']}"
    )

    return df, report


def save_cleaned_data(df: pd.DataFrame, output_path: str = "data/processed/cleaned_jobs.csv") -> Path:
    """
    Saves the cleaned DataFrame to the processed directory.
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    logger.info(f"Saved cleaned dataset: {out} ({len(df)} rows)")
    return out


def load_cleaned_data(path: str = "data/processed/cleaned_jobs.csv") -> Optional[pd.DataFrame]:
    """
    Safely loads the cleaned dataset if available.
    """
    p = Path(path)
    if p.exists() and p.stat().st_size > 0:
        return pd.read_csv(p, low_memory=False)
    return None


def load_sample_data(path: str = "data/sample/sample_jobs.csv") -> pd.DataFrame:
    """
    Convenience function: load the sample CSV and run the clean pipeline.
    """
    df = pd.read_csv(path, low_memory=False)
    clean_df, report = clean_pipeline(df)
    return clean_df
