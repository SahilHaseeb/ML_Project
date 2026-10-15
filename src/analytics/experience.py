"""
src/analytics/experience.py
-----------------------------
Functions for experience-level analysis.
"""

import pandas as pd


def get_experience_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Bucket experience_min into human-readable experience levels.
    Returns a DataFrame with columns: level, count
    """
    if "experience_min" not in df.columns:
        return pd.DataFrame(columns=["level", "count"])

    def bucket(years):
        if pd.isna(years):
            return "Not specified"
        y = float(years)
        if y < 1:
            return "Fresher (< 1 yr)"
        elif y < 3:
            return "Junior (1–2 yrs)"
        elif y < 5:
            return "Mid-level (3–4 yrs)"
        elif y < 8:
            return "Senior (5–7 yrs)"
        else:
            return "Expert (8+ yrs)"

    order = [
        "Fresher (< 1 yr)", "Junior (1–2 yrs)",
        "Mid-level (3–4 yrs)", "Senior (5–7 yrs)", "Expert (8+ yrs)",
        "Not specified",
    ]

    buckets = df["experience_min"].apply(bucket)
    counts = buckets.value_counts().reindex(order, fill_value=0).reset_index()
    counts.columns = ["level", "count"]
    return counts[counts["count"] > 0]


def get_avg_experience_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return average minimum experience required for each job category.
    Columns: category, avg_experience_years
    """
    if "category" not in df.columns or "experience_min" not in df.columns:
        return pd.DataFrame(columns=["category", "avg_experience_years"])

    result = (
        df[df["experience_min"].notna()]
        .groupby("category")["experience_min"]
        .mean()
        .round(1)
        .reset_index()
        .rename(columns={"experience_min": "avg_experience_years"})
        .sort_values("avg_experience_years", ascending=False)
    )
    return result


def get_experience_vs_salary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a scatter-ready DataFrame of experience_min vs salary_min.
    Includes category for color-coding.
    """
    needed = {"experience_min", "salary_min"}
    if not needed.issubset(df.columns):
        return pd.DataFrame()

    return df[["experience_min", "salary_min", "category", "title", "company"]].dropna(
        subset=["experience_min", "salary_min"]
    )
