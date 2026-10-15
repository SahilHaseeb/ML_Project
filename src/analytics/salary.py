"""
src/analytics/salary.py
------------------------
Functions for salary data analysis.

Important: Many job listings do NOT disclose salary.
We always report the coverage rate so readers know how representative
the salary data is — never assume undisclosed salaries equal zero.
"""

import pandas as pd
import numpy as np


def get_salary_coverage(df: pd.DataFrame) -> dict:
    """
    Return how many listings have salary data disclosed.
    """
    total = len(df)
    if "salary_min" not in df.columns:
        return {"disclosed": 0, "total": total, "rate_pct": 0.0}

    disclosed = df["salary_min"].notna().sum()
    return {
        "disclosed": int(disclosed),
        "total": total,
        "rate_pct": round(disclosed / total * 100, 1) if total else 0.0,
    }


def get_salary_stats_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute median, min, and max salary_min for each job category.
    Only includes rows where salary_min is available.
    
    Columns: category, median_salary, min_salary, max_salary, job_count
    """
    required = {"category", "salary_min", "salary_currency"}
    if not required.issubset(df.columns):
        return pd.DataFrame()

    filtered = df[df["salary_min"].notna() & df["salary_currency"].notna()].copy()
    if filtered.empty:
        return pd.DataFrame()

    # Focus on PKR listings for comparability
    pkr = filtered[filtered["salary_currency"] == "PKR"]
    if pkr.empty:
        pkr = filtered  # Fallback to all currencies

    result = (
        pkr.groupby("category")["salary_min"]
        .agg(
            median_salary="median",
            min_salary="min",
            max_salary="max",
            job_count="count",
        )
        .reset_index()
        .sort_values("median_salary", ascending=False)
    )
    return result


def get_salary_distribution(df: pd.DataFrame) -> pd.Series:
    """
    Return all disclosed salary_min values (PKR only) as a Series
    suitable for building a histogram.
    """
    if "salary_min" not in df.columns:
        return pd.Series(dtype="float64")

    pkr_mask = df.get("salary_currency", pd.Series(dtype="str")) == "PKR"
    return df.loc[pkr_mask & df["salary_min"].notna(), "salary_min"].dropna()


def get_salary_by_experience(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group salary_min by experience_min buckets to show the
    salary-experience relationship.
    """
    required = {"salary_min", "experience_min"}
    if not required.issubset(df.columns):
        return pd.DataFrame()

    working = df[df["salary_min"].notna() & df["experience_min"].notna()].copy()
    if working.empty:
        return pd.DataFrame()

    def exp_bucket(years):
        if years < 1:
            return "0 (Fresher)"
        elif years < 3:
            return "1-2 yrs"
        elif years < 5:
            return "3-4 yrs"
        elif years < 8:
            return "5-7 yrs"
        else:
            return "8+ yrs"

    working["exp_bucket"] = working["experience_min"].apply(exp_bucket)
    result = (
        working.groupby("exp_bucket")["salary_min"]
        .median()
        .reset_index()
        .rename(columns={"salary_min": "median_salary"})
    )
    # Order buckets logically
    order = ["0 (Fresher)", "1-2 yrs", "3-4 yrs", "5-7 yrs", "8+ yrs"]
    result["exp_bucket"] = pd.Categorical(result["exp_bucket"], categories=order, ordered=True)
    return result.sort_values("exp_bucket")
