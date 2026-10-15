"""
src/analytics/trends.py
------------------------
Functions for historical and time-series analysis.
Answers questions like: "Are more AI jobs being posted over time?"
"""

import pandas as pd


def get_monthly_posting_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    Count how many jobs were posted per month.
    Returns a DataFrame with columns: month (string), count
    """
    if "posting_date" not in df.columns:
        return pd.DataFrame(columns=["month", "count"])

    dated = df[df["posting_date"].notna()].copy()
    if dated.empty:
        return pd.DataFrame(columns=["month", "count"])

    dated["month"] = dated["posting_date"].dt.to_period("M").astype(str)
    counts = dated.groupby("month").size().reset_index(name="count")
    counts = counts.sort_values("month")
    return counts


def get_category_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return the number of postings per category per month.
    Useful for drawing a multi-line trend chart.
    Columns: month, category, count
    """
    if "posting_date" not in df.columns or "category" not in df.columns:
        return pd.DataFrame(columns=["month", "category", "count"])

    dated = df[df["posting_date"].notna() & df["category"].notna()].copy()
    if dated.empty:
        return pd.DataFrame(columns=["month", "category", "count"])

    dated["month"] = dated["posting_date"].dt.to_period("M").astype(str)
    result = (
        dated.groupby(["month", "category"])
        .size()
        .reset_index(name="count")
        .sort_values(["month", "category"])
    )
    return result


def get_skill_growth(df: pd.DataFrame, skill: str) -> pd.DataFrame:
    """
    Track how many job postings mention a specific skill per month.
    Useful for showing if demand for a skill is rising or falling.
    """
    if "posting_date" not in df.columns or "skills" not in df.columns:
        return pd.DataFrame(columns=["month", "count"])

    dated = df[df["posting_date"].notna()].copy()
    dated["month"] = dated["posting_date"].dt.to_period("M").astype(str)

    def mentions(skills_str):
        if pd.isna(skills_str):
            return False
        return skill.lower() in [s.strip().lower() for s in str(skills_str).split("|")]

    dated["mentions_skill"] = dated["skills"].apply(mentions)
    result = (
        dated[dated["mentions_skill"]]
        .groupby("month")
        .size()
        .reset_index(name="count")
        .sort_values("month")
    )
    return result
