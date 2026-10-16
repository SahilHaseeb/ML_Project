"""
tests/test_collection.py
------------------------
Unit tests for data collectors with mocked network responses.
Ensures collection works offline and extracts raw fields correctly.
"""

import json
from unittest.mock import MagicMock, patch
import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.collection.base import BaseCollector
from src.collection.api_collectors import (
    RemotiveCollector,
    ArbeitnowCollector,
    LocalRawFileCollector,
)
from src.collection.pipeline import CollectionPipeline


class TestRemotiveCollector:
    @patch("requests.Session.get")
    def test_remotive_extracts_raw_records(self, mock_get, tmp_path):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "jobs": [
                {
                    "id": 12345,
                    "url": "https://remotive.com/job/12345",
                    "title": "Backend Python Engineer",
                    "company_name": "Acme Global",
                    "candidate_required_location": "Worldwide",
                    "category": "software-dev",
                    "tags": ["python", "django", "aws"],
                    "job_type": "full_time",
                    "publication_date": "2024-05-10T12:00:00",
                    "salary": "$90,000 - $120,000",
                    "description": "<p>We are hiring a backend developer.</p>",
                }
            ]
        }
        mock_get.return_value = mock_resp

        collector = RemotiveCollector(output_dir=str(tmp_path), rate_limit=0.0)
        records = collector.collect(save_raw=True)

        assert len(records) == 1
        r = records[0]
        assert r["raw_job_id"] == "12345"
        assert r["title_raw"] == "Backend Python Engineer"
        assert r["company_raw"] == "Acme Global"
        assert r["candidate_location_raw"] == "Worldwide"
        assert r["skills_raw"] == "python|django|aws"
        assert r["source"] == "remotive_api"

        # Check raw snapshot was saved to disk
        raw_files = list(tmp_path.glob("remotive_api_raw_*.json"))
        assert len(raw_files) == 1


class TestArbeitnowCollector:
    @patch("requests.Session.get")
    def test_arbeitnow_extracts_raw_records(self, mock_get, tmp_path):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [
                {
                    "slug": "data-analyst-berlin",
                    "company_name": "DataInsights",
                    "title": "Data Analyst",
                    "description": "Looking for a BI specialist.",
                    "remote": False,
                    "url": "https://arbeitnow.com/job/data-analyst",
                    "tags": ["sql", "tableau"],
                    "job_types": ["Full Time"],
                    "location": "Berlin",
                    "created_at": 1715330000,
                }
            ]
        }
        mock_get.return_value = mock_resp

        collector = ArbeitnowCollector(output_dir=str(tmp_path), rate_limit=0.0)
        records = collector.collect(save_raw=True)

        assert len(records) == 1
        r = records[0]
        assert r["raw_job_id"] == "data-analyst-berlin"
        assert r["title_raw"] == "Data Analyst"
        assert r["location_raw"] == "Berlin"
        assert r["source"] == "arbeitnow_api"


class TestLocalRawFileCollector:
    def test_local_file_collection(self, tmp_path):
        # Create a sample raw CSV
        sample_csv = tmp_path / "test_raw.csv"
        df = pd.DataFrame([{
            "job_id": "LOC-01",
            "title": "Senior Flutter Developer",
            "company": "PakTech",
            "location": "Lahore",
            "source": "pk_open_feed",
        }])
        df.to_csv(sample_csv, index=False)

        collector = LocalRawFileCollector(file_path=str(sample_csv), output_dir=str(tmp_path))
        records = collector.collect(save_raw=False)

        assert len(records) == 1
        assert records[0]["title_raw"] == "Senior Flutter Developer"
        assert records[0]["company_raw"] == "PakTech"
        assert records[0]["location_raw"] == "Lahore"
