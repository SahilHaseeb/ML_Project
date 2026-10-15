"""
src/analytics/location.py
---------------------------
Functions for geographic distribution analysis.
"""

import pandas as pd


def get_jobs_by_city(df: pd.DataFrame) -> pd.DataFrame:
    """
    Count job listings per city.
    Columns: location, count, percentage
    """
    if "location" not in df.columns:
        return pd.DataFrame(columns=["location", "count", "percentage"])

    counts = df["location"].dropna().value_counts().reset_index()
    counts.columns = ["location", "count"]
    total = counts["count"].sum()
    counts["percentage"] = (counts["count"] / total * 100).round(1)
    return counts


def get_remote_vs_onsite(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify each listing as Remote, Hybrid, or On-site and return counts.
    """
    if "location" not in df.columns:
        return pd.DataFrame(columns=["work_mode", "count"])

    def classify(loc):
        if pd.isna(loc):
            return "Unknown"
        loc_str = str(loc).lower()
        if "remote" in loc_str:
            return "Remote"
        if "hybrid" in loc_str:
            return "Hybrid"
        return "On-site"

    mode_counts = df["location"].apply(classify).value_counts().reset_index()
    mode_counts.columns = ["work_mode", "count"]
    return mode_counts


def get_top_cities(df: pd.DataFrame, n: int = 8) -> pd.DataFrame:
    """Return the n cities with the most listings."""
    all_cities = get_jobs_by_city(df)
    # Exclude Remote/Hybrid from city ranking
    city_df = all_cities[~all_cities["location"].isin(["Remote", "Hybrid", "Unknown"])]
    return city_df.head(n).reset_index(drop=True)


def get_categories_by_city(df: pd.DataFrame, city: str) -> pd.DataFrame:
    """Return the job category distribution for a specific city."""
    if "category" not in df.columns or "location" not in df.columns:
        return pd.DataFrame(columns=["category", "count"])

    filtered = df[df["location"] == city]
    if filtered.empty:
        return pd.DataFrame(columns=["category", "count"])

    counts = filtered["category"].dropna().value_counts().reset_index()
    counts.columns = ["category", "count"]
    return counts
