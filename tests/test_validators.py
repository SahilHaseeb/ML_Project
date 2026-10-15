"""
tests/test_validators.py
-------------------------
Unit tests for the data validation module.

Run with:  pytest tests/ -v
"""

import pandas as pd
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_processing.validators import (
    validate_required_columns,
    validate_date_column,
    validate_numeric_range,
    generate_quality_report,
)


# ── Fixtures (reusable sample DataFrames) ─────────────────────────────────────
@pytest.fixture
def valid_df():
    """A minimal DataFrame that passes all required column checks."""
    return pd.DataFrame({
        "job_id": ["J001", "J002"],
        "title": ["Python Dev", "Data Scientist"],
        "source": ["sample", "sample"],
        "scraped_at": ["2024-01-01", "2024-01-02"],
        "salary_min": [80000.0, 100000.0],
        "salary_max": [120000.0, 150000.0],
        "experience_min": [2.0, 3.0],
        "experience_max": [4.0, 5.0],
        "posting_date": ["2024-01-01", "not-a-date"],
    })


@pytest.fixture
def missing_col_df():
    """A DataFrame missing the required 'job_id' column."""
    return pd.DataFrame({
        "title": ["Dev"],
        "source": ["sample"],
        "scraped_at": ["2024-01-01"],
    })


# ── Tests ──────────────────────────────────────────────────────────────────────
class TestValidateRequiredColumns:
    def test_passes_with_all_required_columns(self, valid_df):
        is_valid, missing = validate_required_columns(valid_df)
        assert is_valid is True
        assert missing == []

    def test_fails_when_column_is_missing(self, missing_col_df):
        is_valid, missing = validate_required_columns(missing_col_df)
        assert is_valid is False
        assert "job_id" in missing

    def test_empty_dataframe_still_passes_column_check(self):
        """An empty DataFrame with the right columns should still pass."""
        df = pd.DataFrame(columns=["job_id", "title", "source", "scraped_at"])
        is_valid, missing = validate_required_columns(df)
        assert is_valid is True


class TestValidateDateColumn:
    def test_valid_dates_are_parsed(self, valid_df):
        result = validate_date_column(valid_df, "posting_date")
        # J001's date should be valid
        assert pd.notna(result.loc[0, "posting_date"])

    def test_invalid_dates_become_nat(self, valid_df):
        result = validate_date_column(valid_df, "posting_date")
        # J002's "not-a-date" should become NaT
        assert pd.isna(result.loc[1, "posting_date"])

    def test_missing_column_is_ignored(self, valid_df):
        """Should not crash if the column doesn't exist."""
        result = validate_date_column(valid_df, "nonexistent_column")
        assert "nonexistent_column" not in result.columns


class TestValidateNumericRange:
    def test_valid_ranges_are_unchanged(self, valid_df):
        result = validate_numeric_range(valid_df, "salary_min", "salary_max")
        assert result.loc[0, "salary_min"] == 80000.0
        assert result.loc[0, "salary_max"] == 120000.0

    def test_invalid_range_becomes_nan(self):
        """When min > max, both values should be set to NaN."""
        df = pd.DataFrame({
            "job_id": ["J001"],
            "title": ["Dev"],
            "source": ["s"],
            "scraped_at": ["2024-01-01"],
            "salary_min": [200000.0],
            "salary_max": [100000.0],   # max < min → invalid
        })
        result = validate_numeric_range(df, "salary_min", "salary_max")
        assert pd.isna(result.loc[0, "salary_min"])
        assert pd.isna(result.loc[0, "salary_max"])

    def test_missing_column_is_ignored(self, valid_df):
        """Should not crash if columns are absent."""
        result = validate_numeric_range(valid_df, "nonexistent_min", "nonexistent_max")
        assert result is not None


class TestGenerateQualityReport:
    def test_report_structure(self, valid_df):
        report = generate_quality_report(valid_df)
        assert "total_rows" in report
        assert "missing_values" in report
        assert "completeness_pct" in report

    def test_total_rows_correct(self, valid_df):
        report = generate_quality_report(valid_df)
        assert report["total_rows"] == 2

    def test_completeness_is_100_for_complete_column(self, valid_df):
        report = generate_quality_report(valid_df)
        assert report["completeness_pct"]["job_id"] == 100.0
