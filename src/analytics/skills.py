"""
src/analytics/skills.py
-------------------------
Functions that calculate skill-related statistics.

Key concept: skills are stored as pipe-separated strings per row, e.g.:
    "Python|Django|REST API|PostgreSQL"

We need to "explode" these into individual rows before counting,
otherwise we would count "Python|Django" as one skill instead of two.
"""

import pandas as pd
from collections import Counter


def _explode_skills(df: pd.DataFrame, col: str = "skills") -> pd.Series:
    """
    Split the pipe-separated skills column and return a flat Series
    where every element is one individual skill.

    Example:
        Row 1: "Python|Django"
        Row 2: "Python|SQL"
        → Series: ["Python", "Django", "Python", "SQL"]
    """
    if col not in df.columns:
        return pd.Series(dtype="object")

    all_skills = []
    for value in df[col].dropna():
        for skill in str(value).split("|"):
            skill = skill.strip()
            if skill:
                all_skills.append(skill)
    return pd.Series(all_skills)


def get_top_skills(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """
    Return the top-n most frequently requested skills.

    Columns: skill, count, percentage
    """
    skill_series = _explode_skills(df)
    if skill_series.empty:
        return pd.DataFrame(columns=["skill", "count", "percentage"])

    counts = skill_series.value_counts().head(n).reset_index()
    counts.columns = ["skill", "count"]
    total_jobs = len(df)
    counts["percentage"] = (counts["count"] / total_jobs * 100).round(1)
    return counts


def get_skills_by_category(
    df: pd.DataFrame,
    category: str,
    n: int = 10,
) -> pd.DataFrame:
    """
    Return the top-n skills for a specific job category.

    Parameters
    ----------
    df : clean DataFrame
    category : the category name to filter on (e.g. "Data Science")
    n : how many top skills to return
    """
    if "category" not in df.columns:
        return pd.DataFrame(columns=["skill", "count"])

    filtered = df[df["category"] == category]
    if filtered.empty:
        return pd.DataFrame(columns=["skill", "count"])

    skill_series = _explode_skills(filtered)
    counts = skill_series.value_counts().head(n).reset_index()
    counts.columns = ["skill", "count"]
    return counts


def get_skill_category_matrix(df: pd.DataFrame, top_n_skills: int = 15) -> pd.DataFrame:
    """
    Build a pivot table: rows = categories, columns = top skills, values = count.
    
    This is used to draw a heatmap showing which skills appear in which categories.
    """
    if "category" not in df.columns or "skills" not in df.columns:
        return pd.DataFrame()

    # Get the top skills overall first
    top_skills = get_top_skills(df, n=top_n_skills)["skill"].tolist()

    rows = []
    for _, row in df.iterrows():
        cat = row.get("category")
        skills_str = row.get("skills")
        if pd.isna(cat) or pd.isna(skills_str):
            continue
        job_skills = {s.strip() for s in str(skills_str).split("|")}
        for skill in top_skills:
            rows.append({"category": cat, "skill": skill, "present": skill in job_skills})

    if not rows:
        return pd.DataFrame()

    long_df = pd.DataFrame(rows)
    matrix = long_df.pivot_table(
        index="category", columns="skill", values="present", aggfunc="sum", fill_value=0
    )
    return matrix


def get_unique_skill_count(df: pd.DataFrame) -> int:
    """Return the total number of distinct skills in the dataset."""
    skill_series = _explode_skills(df)
    return skill_series.nunique()
