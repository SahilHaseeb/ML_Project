"""
tests/test_analytics.py
------------------------
Unit tests for the analytics modules (overview, skills, location, salary, experience, trends).
"""

import pandas as pd
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.analytics.overview import get_total_jobs, get_unique_companies, get_salary_disclosure_rate, get_summary_stats
from src.analytics.skills import get_top_skills, get_unique_skill_count
from src.analytics.location import get_jobs_by_city, get_remote_vs_onsite
from src.analytics.salary import get_salary_coverage
from src.analytics.experience import get_experience_distribution
from src.analytics.trends import get_monthly_posting_trend


@pytest.fixture
def sample_df():
    """A small representative DataFrame for testing analytics functions."""
    return pd.DataFrame({
        "job_id": ["J1", "J2", "J3", "J4"],
        "title": ["Python Dev", "Data Sci", "ML Eng", "QA"],
        "company": ["A", "B", "A", "C"],
        "location": ["Lahore", "Karachi", "Remote", "Lahore"],
        "category": ["Software Development", "Data Science", "Machine Learning", "Quality Assurance"],
        "salary_min": [80000.0, 100000.0, None, 50000.0],
        "salary_max": [120000.0, 150000.0, None, 70000.0],
        "salary_currency": ["PKR", "PKR", None, "PKR"],
        "experience_min": [2.0, 3.0, 5.0, 1.0],
        "experience_max": [4.0, 5.0, 7.0, 2.0],
        "skills": ["Python|Django", "Python|Pandas|SQL", "TensorFlow|PyTorch", "Selenium|Python"],
        "posting_date": pd.to_datetime(["2024-01-15", "2024-02-10", "2024-02-20", "2024-03-05"]),
        "source": ["sample"] * 4,
        "scraped_at": pd.to_datetime(["2024-10-01"] * 4),
        "job_type": ["Full-time"] * 4,
    })


class TestOverviewAnalytics:
    def test_total_jobs(self, sample_df):
        assert get_total_jobs(sample_df) == 4

    def test_unique_companies(self, sample_df):
        assert get_unique_companies(sample_df) == 3  # A, B, C

    def test_salary_disclosure_rate(self, sample_df):
        # 3 out of 4 have salary_min
        rate = get_salary_disclosure_rate(sample_df)
        assert rate == 75.0

    def test_summary_stats_keys(self, sample_df):
        stats = get_summary_stats(sample_df)
        for key in ["total_jobs", "unique_companies", "unique_cities", "remote_jobs"]:
            assert key in stats


class TestSkillsAnalytics:
    def test_top_skills_returns_dataframe(self, sample_df):
        df = get_top_skills(sample_df, n=10)
        assert isinstance(df, pd.DataFrame)
        assert "skill" in df.columns
        assert "count" in df.columns

    def test_python_is_top_skill(self, sample_df):
        """Python appears in 3 of 4 rows, so it should be #1."""
        df = get_top_skills(sample_df, n=5)
        assert df.iloc[0]["skill"] == "Python"
        assert df.iloc[0]["count"] == 3

    def test_unique_skill_count(self, sample_df):
        count = get_unique_skill_count(sample_df)
        # Skills: Python, Django, Pandas, SQL, TensorFlow, PyTorch, Selenium = 7
        assert count == 7


class TestLocationAnalytics:
    def test_jobs_by_city(self, sample_df):
        df = get_jobs_by_city(sample_df)
        assert not df.empty
        assert "location" in df.columns
        assert "count" in df.columns

    def test_lahore_has_2_jobs(self, sample_df):
        df = get_jobs_by_city(sample_df)
        lahore_row = df[df["location"] == "Lahore"]
        assert lahore_row["count"].iloc[0] == 2

    def test_remote_vs_onsite(self, sample_df):
        df = get_remote_vs_onsite(sample_df)
        assert "work_mode" in df.columns
        remote_row = df[df["work_mode"] == "Remote"]
        assert remote_row["count"].iloc[0] == 1


class TestSalaryAnalytics:
    def test_salary_coverage(self, sample_df):
        cov = get_salary_coverage(sample_df)
        assert cov["disclosed"] == 3
        assert cov["total"] == 4
        assert cov["rate_pct"] == 75.0


class TestExperienceAnalytics:
    def test_experience_distribution(self, sample_df):
        df = get_experience_distribution(sample_df)
        assert not df.empty
        assert "level" in df.columns
        assert "count" in df.columns

    def test_all_rows_bucketed(self, sample_df):
        df = get_experience_distribution(sample_df)
        assert df["count"].sum() == 4


class TestTrendsAnalytics:
    def test_monthly_trend(self, sample_df):
        df = get_monthly_posting_trend(sample_df)
        assert not df.empty
        assert "month" in df.columns
        assert "count" in df.columns

    def test_monthly_trend_sums_to_total(self, sample_df):
        df = get_monthly_posting_trend(sample_df)
        assert df["count"].sum() == 4
