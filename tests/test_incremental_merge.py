"""
tests/test_incremental_merge.py
--------------------------------
Unit tests for safe incremental dataset merging and anti-data-loss protections.
All tests use temporary paths and mocked collector responses (no live network calls).
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pandas as pd
import pytest

from src.data_processing.cleaner import (
    merge_cleaned_datasets,
    safe_incremental_save,
    load_cleaned_data,
)
from src.collection.runner import run_collection


@pytest.fixture
def sample_existing_df():
    """Returns a minimal valid cleaned DataFrame representing existing historical jobs."""
    return pd.DataFrame([
        {
            "job_id": "COL-0001",
            "title": "Machine Learning Engineer",
            "company": "PakAI Solutions",
            "location": "Lahore",
            "candidate_location": "Lahore",
            "location_scope": "Pakistan (On-site / Hybrid)",
            "category": "Data Science / AI",
            "salary_min": 150000.0,
            "salary_max": 250000.0,
            "salary_currency": "PKR",
            "experience_min": 2.0,
            "experience_max": 4.0,
            "education": "Bachelor",
            "job_type": "Full-time",
            "skills": "Python|PyTorch|Scikit-learn",
            "description": "Develop and deploy ML models.",
            "posting_date": "2024-05-01",
            "source": "arbeitnow_api",
            "job_url": "https://example.com/job/ml-engineer-01",
            "scraped_at": "2024-05-02T10:00:00Z",
        },
        {
            "job_id": "COL-0002",
            "title": "Senior Python Backend Developer",
            "company": "CloudGrid",
            "location": "Remote",
            "candidate_location": "Worldwide",
            "location_scope": "Worldwide Remote (Pakistan-Eligible)",
            "category": "Software Development",
            "salary_min": 3000.0,
            "salary_max": 5000.0,
            "salary_currency": "USD",
            "experience_min": 5.0,
            "experience_max": 8.0,
            "education": None,
            "job_type": "Full-time",
            "skills": "Python|FastAPI|Docker|PostgreSQL",
            "description": "Build high-throughput APIs.",
            "posting_date": "2024-05-03",
            "source": "remotive_api",
            "job_url": "https://example.com/job/backend-dev-02",
            "scraped_at": "2024-05-04T12:00:00Z",
        },
    ])


@pytest.fixture
def sample_new_df():
    """Returns a new batch containing 1 duplicate of job 2 and 1 brand new job."""
    return pd.DataFrame([
        {
            "job_id": "COL-0002",
            "title": "Senior Python Backend Developer",
            "company": "CloudGrid",
            "location": "Remote",
            "candidate_location": "Worldwide",
            "location_scope": "Worldwide Remote (Pakistan-Eligible)",
            "category": "Software Development",
            "salary_min": 3000.0,
            "salary_max": 5000.0,
            "salary_currency": "USD",
            "experience_min": 5.0,
            "experience_max": 8.0,
            "education": None,
            "job_type": "Full-time",
            "skills": "Python|FastAPI|Docker|PostgreSQL",
            "description": "Build high-throughput APIs.",
            "posting_date": "2024-05-03",
            "source": "remotive_api",
            "job_url": "https://example.com/job/backend-dev-02",  # Duplicate URL
            "scraped_at": "2024-05-10T12:00:00Z",
        },
        {
            "job_id": "COL-0003",
            "title": "Data Engineer",
            "company": "DataStream Pak",
            "location": "Karachi",
            "candidate_location": "Karachi",
            "location_scope": "Pakistan (On-site / Hybrid)",
            "category": "Data Science / AI",
            "salary_min": 180000.0,
            "salary_max": 280000.0,
            "salary_currency": "PKR",
            "experience_min": 3.0,
            "experience_max": 5.0,
            "education": "Bachelor",
            "job_type": "Full-time",
            "skills": "Python|SQL|Spark|Airflow",
            "description": "Build ETL data pipelines.",
            "posting_date": "2024-05-10",
            "source": "arbeitnow_api",
            "job_url": "https://example.com/job/data-engineer-03",  # Genuinely new URL
            "scraped_at": "2024-05-10T12:00:00Z",
        },
    ])


class TestMergeCleanedDatasets:
    def test_preserves_existing_when_new_is_empty(self, sample_existing_df):
        merged = merge_cleaned_datasets(sample_existing_df, pd.DataFrame())
        assert len(merged) == len(sample_existing_df)
        assert list(merged["job_id"]) == ["COL-0001", "COL-0002"]

    def test_preserves_existing_when_new_is_none(self, sample_existing_df):
        merged = merge_cleaned_datasets(sample_existing_df, None)
        assert len(merged) == len(sample_existing_df)
        assert list(merged["job_id"]) == ["COL-0001", "COL-0002"]

    def test_preserves_new_when_existing_is_empty(self, sample_new_df):
        merged = merge_cleaned_datasets(pd.DataFrame(), sample_new_df)
        assert len(merged) == len(sample_new_df)
        assert "COL-0003" in list(merged["job_id"])

    def test_preserves_new_when_existing_is_none(self, sample_new_df):
        merged = merge_cleaned_datasets(None, sample_new_df)
        assert len(merged) == len(sample_new_df)

    def test_both_empty_returns_empty_dataframe(self):
        merged = merge_cleaned_datasets(pd.DataFrame(), pd.DataFrame())
        assert merged.empty

    def test_appends_distinct_records_and_deduplicates(self, sample_existing_df, sample_new_df):
        # Existing has 2 jobs (job1, job2). New has 2 jobs (job2, job3).
        # Expected result: exactly 3 jobs (job1, job2, job3).
        merged = merge_cleaned_datasets(sample_existing_df, sample_new_df)
        assert len(merged) == 3
        urls = list(merged["job_url"])
        assert "https://example.com/job/ml-engineer-01" in urls
        assert "https://example.com/job/backend-dev-02" in urls
        assert "https://example.com/job/data-engineer-03" in urls

    def test_preserves_historical_job_scraped_at_timestamp(self, sample_existing_df, sample_new_df):
        # Because existing records come first, job2's original scraped_at (2024-05-04) is preserved
        merged = merge_cleaned_datasets(sample_existing_df, sample_new_df)
        job2 = merged[merged["job_url"] == "https://example.com/job/backend-dev-02"].iloc[0]
        assert job2["scraped_at"] == "2024-05-04T12:00:00Z"

    def test_deduplicates_by_fingerprint_when_urls_are_missing(self):
        existing = pd.DataFrame([{
            "job_id": "COL-01",
            "title": "Django Developer",
            "company": "SoftCorp",
            "location": "Islamabad",
            "posting_date": "2024-05-01",
            "job_url": None,
        }])
        new = pd.DataFrame([{
            "job_id": "COL-02",
            "title": "django developer",  # Case difference
            "company": "softcorp",
            "location": "islamabad",
            "posting_date": "2024-05-01",
            "job_url": None,
        }])
        merged = merge_cleaned_datasets(existing, new)
        assert len(merged) == 1
        assert merged.iloc[0]["job_id"] == "COL-01"


class TestSafeIncrementalSave:
    def test_creates_new_file_when_none_exists(self, tmp_path, sample_new_df):
        target = tmp_path / "cleaned_jobs.csv"
        out_path, total, added = safe_incremental_save(sample_new_df, output_path=str(target))
        assert out_path.exists()
        assert total == 2
        assert added == 2
        loaded = pd.read_csv(target)
        assert len(loaded) == 2

    def test_never_overwrites_existing_file_when_new_is_empty(self, tmp_path, sample_existing_df):
        target = tmp_path / "cleaned_jobs.csv"
        sample_existing_df.to_csv(target, index=False)

        # Call with empty DataFrame
        out_path, total, added = safe_incremental_save(pd.DataFrame(), output_path=str(target))
        assert total == 2
        assert added == 0

        # Verify disk contents are untouched
        loaded = pd.read_csv(target)
        assert len(loaded) == 2
        assert list(loaded["job_id"]) == ["COL-0001", "COL-0002"]

    def test_never_overwrites_existing_file_when_new_is_none(self, tmp_path, sample_existing_df):
        target = tmp_path / "cleaned_jobs.csv"
        sample_existing_df.to_csv(target, index=False)

        out_path, total, added = safe_incremental_save(None, output_path=str(target))
        assert total == 2
        assert added == 0
        loaded = pd.read_csv(target)
        assert len(loaded) == 2

    def test_incremental_merge_appends_and_saves_to_disk(self, tmp_path, sample_existing_df, sample_new_df):
        target = tmp_path / "cleaned_jobs.csv"
        sample_existing_df.to_csv(target, index=False)

        out_path, total, added = safe_incremental_save(sample_new_df, output_path=str(target))
        assert total == 3
        assert added == 1

        loaded = pd.read_csv(target)
        assert len(loaded) == 3
        # Ensure temporary file was cleanly removed
        assert not target.with_suffix(".csv.tmp").exists()

    def test_shrink_detection_raises_error_and_preserves_file(self, tmp_path, sample_existing_df):
        target = tmp_path / "cleaned_jobs.csv"
        sample_existing_df.to_csv(target, index=False)

        # Mock merge_cleaned_datasets to return fewer rows than existing
        with patch("src.data_processing.cleaner.merge_cleaned_datasets", return_value=sample_existing_df.iloc[:1]):
            with pytest.raises(ValueError, match="Dataset shrink detected"):
                safe_incremental_save(sample_existing_df, output_path=str(target))

        # Original file remains preserved
        loaded = pd.read_csv(target)
        assert len(loaded) == 2


class TestRunnerFailureHandling:
    def test_runner_preserves_existing_dataset_on_pipeline_exception(self, tmp_path, sample_existing_df):
        target = tmp_path / "cleaned_jobs.csv"
        sample_existing_df.to_csv(target, index=False)

        # Mock pipeline.run to simulate network / API crash
        with patch("src.collection.runner.CollectionPipeline.run", side_effect=RuntimeError("API Gateway Timeout")):
            result = run_collection(
                output_path=str(target),
                raw_dir=str(tmp_path / "raw"),
                merge_existing=True,
            )

        assert result["status"] == "preserved"
        assert result["total_jobs"] == 2
        assert result["added"] == 0

        # Existing dataset on disk remains completely intact
        loaded = pd.read_csv(target)
        assert len(loaded) == 2

    def test_runner_preserves_existing_dataset_when_apis_return_empty(self, tmp_path, sample_existing_df):
        target = tmp_path / "cleaned_jobs.csv"
        sample_existing_df.to_csv(target, index=False)

        with patch("src.collection.runner.CollectionPipeline.run", return_value=pd.DataFrame()):
            result = run_collection(
                output_path=str(target),
                raw_dir=str(tmp_path / "raw"),
                merge_existing=True,
            )

        assert result["status"] == "preserved"
        assert result["total_jobs"] == 2
        assert result["added"] == 0

        loaded = pd.read_csv(target)
        assert len(loaded) == 2

    def test_runner_merges_new_jobs_when_collection_succeeds(self, tmp_path, sample_existing_df):
        target = tmp_path / "cleaned_jobs.csv"
        sample_existing_df.to_csv(target, index=False)

        # Mock raw dataframe with 1 duplicate and 1 brand new job
        raw_mock = pd.DataFrame([
            {
                "raw_job_id": "COL-0002",
                "title_raw": "Senior Python Backend Developer",
                "company_raw": "CloudGrid",
                "location_raw": "Remote",
                "candidate_location_raw": "Worldwide",
                "salary_raw": "$3,000 - $5,000",
                "category_raw": "Software Development",
                "job_type_raw": "Full-time",
                "skills_raw": "Python|FastAPI|Docker",
                "description_raw": "API developer role",
                "posting_date_raw": "2024-05-03",
                "job_url": "https://example.com/job/backend-dev-02",  # Duplicate of existing
                "source": "remotive_api",
                "collected_at": "2024-05-15T00:00:00Z",
            },
            {
                "raw_job_id": "COL-9999",
                "title_raw": "Lead AI Researcher",
                "company_raw": "DeepVision Pak",
                "location_raw": "Lahore",
                "candidate_location_raw": "Lahore",
                "salary_raw": "300k - 450k PKR",
                "category_raw": "Data Science / AI",
                "job_type_raw": "Full-time",
                "skills_raw": "Python|PyTorch|Transformers",
                "description_raw": "Lead generative AI research.",
                "posting_date_raw": "2024-05-15",
                "job_url": "https://example.com/job/lead-ai-9999",  # Brand new
                "source": "arbeitnow_api",
                "collected_at": "2024-05-15T00:00:00Z",
            },
        ])

        with patch("src.collection.runner.CollectionPipeline.run", return_value=raw_mock):
            result = run_collection(
                output_path=str(target),
                raw_dir=str(tmp_path / "raw"),
                merge_existing=True,
            )

        assert result["status"] == "success"
        assert result["total_jobs"] == 3
        assert result["added"] == 1

        loaded = pd.read_csv(target)
        assert len(loaded) == 3
        assert "COL-9999" in list(loaded["job_id"])
