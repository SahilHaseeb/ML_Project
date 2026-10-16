"""
tests/test_cleaner.py
---------------------
Unit tests for Phase 2 data cleaning, standardization, and deduplication.
"""

import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_processing.normalizers import (
    clean_job_title,
    clean_company_name,
    classify_location_scope,
    parse_experience_years,
    parse_salary,
    infer_category,
)
from src.data_processing.cleaner import (
    deduplicate,
    standardize_raw_dataframe,
    clean_pipeline,
)


class TestTitleAndCompanyCleaning:
    def test_clean_job_title_bracket_stripping(self):
        assert clean_job_title("Senior Python Developer [Remote]") == "Senior Python Developer"
        assert clean_job_title("DevOps Engineer (m/f/d)") == "DevOps Engineer"
        assert clean_job_title("Urgent: Data Scientist (Remote)") == "Data Scientist"

    def test_clean_job_title_empty_or_none(self):
        assert clean_job_title("") == ""
        assert clean_job_title(None) == ""

    def test_clean_company_name_suffix_stripping(self):
        assert clean_company_name("TechCorp Pvt Ltd") == "TechCorp"
        assert clean_company_name("DataSoft Private Limited") == "DataSoft"
        assert clean_company_name("CloudSys Inc.") == "CloudSys"
        assert clean_company_name("Nexus LLC") == "Nexus"

    def test_clean_company_name_preserves_plain_name(self):
        assert clean_company_name("Google") == "Google"
        assert clean_company_name("Systems Limited") == "Systems"


class TestLocationScopeClassification:
    def test_pakistan_physical_location(self):
        assert classify_location_scope("Lahore") == "Pakistan (On-site / Hybrid)"
        assert classify_location_scope("Karachi, Pakistan") == "Pakistan (On-site / Hybrid)"
        assert classify_location_scope("Islamabad") == "Pakistan (On-site / Hybrid)"

    def test_pakistan_remote(self):
        assert classify_location_scope("Lahore (Remote)") == "Pakistan (Remote / Hybrid)"
        assert classify_location_scope("Remote", "Pakistan") == "Pakistan (Remote / Hybrid)"

    def test_worldwide_remote_is_pakistan_eligible(self):
        assert classify_location_scope("Remote", "Worldwide") == "Pakistan-Eligible (Worldwide Remote)"
        assert classify_location_scope("Anywhere", "Worldwide") == "Pakistan-Eligible (Worldwide Remote)"
        assert classify_location_scope("Remote (Worldwide)") == "Pakistan-Eligible (Worldwide Remote)"

    def test_restricted_remote_is_not_pakistan_based(self):
        assert classify_location_scope("Remote", "USA Only") == "Restricted Remote (Non-Pakistan)"
        assert classify_location_scope("Remote", "Europe") == "Restricted Remote (Non-Pakistan)"
        assert classify_location_scope("Remote", "UK Only") == "Restricted Remote (Non-Pakistan)"

    def test_international_physical_location(self):
        assert classify_location_scope("Berlin, Germany") == "International (On-site)"
        assert classify_location_scope("London, UK") == "International (On-site)"

    def test_never_labels_unsupported_location_as_pakistan(self):
        scope = classify_location_scope("San Francisco, CA")
        assert "Pakistan" not in scope


class TestSalaryAndExperienceParsing:
    def test_parse_salary_range_pkr(self):
        s_min, s_max, curr = parse_salary("150k - 250k PKR")
        assert s_min == 150000.0
        assert s_max == 250000.0
        assert curr == "PKR"

    def test_parse_salary_usd(self):
        s_min, s_max, curr = parse_salary("$100,000 - $130,000")
        assert s_min == 100000.0
        assert s_max == 130000.0
        assert curr == "USD"

    def test_parse_salary_undisclosed_returns_none(self):
        s_min, s_max, curr = parse_salary("Competitive salary")
        assert s_min is None
        assert s_max is None
        assert curr is None

    def test_parse_salary_empty_returns_none(self):
        assert parse_salary(None) == (None, None, None)
        assert parse_salary("") == (None, None, None)

    def test_parse_experience_range(self):
        e_min, e_max = parse_experience_years("Requires 3-5 years of experience")
        assert e_min == 3.0
        assert e_max == 5.0

    def test_parse_experience_minimum(self):
        e_min, e_max = parse_experience_years("Minimum 4 years required")
        assert e_min == 4.0
        assert e_max is None

    def test_parse_experience_fresh(self):
        e_min, e_max = parse_experience_years("Fresh graduates welcome to apply")
        assert e_min == 0.0
        assert e_max == 1.0

    def test_parse_experience_unknown_returns_none(self):
        assert parse_experience_years("Great communication skills") == (None, None)


class TestDeduplicationAndPipeline:
    def test_deduplicate_removes_duplicate_by_url(self):
        df = pd.DataFrame({
            "job_id": ["1", "2"],
            "title": ["Dev", "Dev"],
            "company": ["Co", "Co"],
            "location": ["Lahore", "Lahore"],
            "posting_date": ["2024-01-01", "2024-01-01"],
            "job_url": ["https://example.com/job1", "https://example.com/job1"],
        })
        deduped = deduplicate(df)
        assert len(deduped) == 1

    def test_deduplicate_removes_duplicate_by_fingerprint(self):
        df = pd.DataFrame({
            "job_id": ["1", "2"],
            "title": ["Python Dev", "python dev"],
            "company": ["Tech Corp", "tech corp"],
            "location": ["Karachi", "karachi"],
            "posting_date": ["2024-01-01", "2024-01-01"],
            "job_url": [None, None],
        })
        deduped = deduplicate(df)
        assert len(deduped) == 1

    def test_clean_pipeline_end_to_end_on_raw_data(self):
        raw_df = pd.DataFrame([{
            "raw_job_id": "RAW-01",
            "title_raw": "Senior Python Developer [Remote]",
            "company_raw": "AlphaTech Pvt Ltd",
            "location_raw": "Lahore",
            "candidate_location_raw": "Worldwide",
            "salary_raw": "120k - 180k PKR",
            "category_raw": "Software Development",
            "job_type_raw": "Full-time",
            "skills_raw": "Python|Django|PostgreSQL",
            "description_raw": "Minimum 3 years of Python experience required.",
            "posting_date_raw": "2024-05-01",
            "job_url": "https://example.com/job/raw-01",
            "source": "test_collector",
            "collected_at": "2024-05-02T10:00:00Z",
        }])

        clean_df, report = clean_pipeline(raw_df)
        assert len(clean_df) == 1
        assert clean_df.loc[0, "title"] == "Senior Python Developer"
        assert clean_df.loc[0, "company"] == "AlphaTech"
        assert clean_df.loc[0, "location_scope"] == "Pakistan (On-site / Hybrid)"
        assert clean_df.loc[0, "salary_min"] == 120000.0
        assert clean_df.loc[0, "salary_max"] == 180000.0
        assert clean_df.loc[0, "salary_currency"] == "PKR"
        assert clean_df.loc[0, "experience_min"] == 3.0
        assert report["total_rows"] == 1
