"""
src/analytics/overview.py
---------------------------
Computes high-level KPI metrics for the Home / Market Overview page.

All functions take a clean DataFrame and return plain Python values
or small DataFrames — no Streamlit code lives here.
This separation makes it easy to unit-test the logic independently.
"""

from typing import Optional
import pandas as pd


def get_total_jobs(df: pd.DataFrame) -> int:
    """Return the number of unique job listings."""
    return len(df)


def get_unique_companies(df: pd.DataFrame) -> int:
    """Return the number of distinct companies in the dataset."""
    if "company" not in df.columns:
        return 0
    return df["company"].dropna().nunique()


def get_unique_cities(df: pd.DataFrame) -> int:
    """Return the number of distinct cities represented."""
    if "location" not in df.columns:
        return 0
    return df["location"].dropna().nunique()


def get_unique_categories(df: pd.DataFrame) -> int:
    """Return the number of distinct job categories."""
    if "category" not in df.columns:
        return 0
    return df["category"].dropna().nunique()


def get_jobs_with_salary(df: pd.DataFrame) -> int:
    """Count how many listings have at least one salary value disclosed."""
    if "salary_min" not in df.columns:
        return 0
    return df["salary_min"].notna().sum()


def get_salary_disclosure_rate(df: pd.DataFrame) -> float:
    """Return the percentage of listings that include salary information."""
    total = len(df)
    if total == 0:
        return 0.0
    return round(get_jobs_with_salary(df) / total * 100, 1)


def get_remote_jobs(df: pd.DataFrame) -> int:
    """Count listings that are tagged as Remote or Hybrid."""
    if "location" not in df.columns:
        return 0
    return df["location"].isin(["Remote", "Hybrid"]).sum()


def get_top_categories(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """
    Return a DataFrame of the top-n job categories by listing count.
    
    Columns: category, count
    """
    if "category" not in df.columns:
        return pd.DataFrame(columns=["category", "count"])
    counts = (
        df["category"]
        .dropna()
        .value_counts()
        .head(n)
        .reset_index()
    )
    counts.columns = ["category", "count"]
    return counts


def get_date_range(df: pd.DataFrame) -> tuple[Optional[str], Optional[str]]:
    """Return the (earliest, latest) posting dates as strings."""
    if "posting_date" not in df.columns:
        return None, None
    dates = df["posting_date"].dropna()
    if dates.empty:
        return None, None
    return str(dates.min().date()), str(dates.max().date())


def get_summary_stats(df: pd.DataFrame) -> dict:
    """
    Aggregate all overview KPIs into a single dictionary.
    Convenient for passing into a Streamlit page.
    """
    earliest, latest = get_date_range(df)
    return {
        "total_jobs": get_total_jobs(df),
        "unique_companies": get_unique_companies(df),
        "unique_cities": get_unique_cities(df),
        "unique_categories": get_unique_categories(df),
        "remote_jobs": get_remote_jobs(df),
        "salary_disclosure_rate": get_salary_disclosure_rate(df),
        "date_range_start": earliest,
        "date_range_end": latest,
        "top_categories": get_top_categories(df),
    }
