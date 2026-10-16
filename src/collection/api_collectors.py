"""
src/collection/api_collectors.py
--------------------------------
Concrete collectors for permitted public job APIs and local raw feeds.

Supported Sources:
1. Remotive API (Remote tech jobs, public developer API).
2. Arbeitnow API (European and remote tech jobs, free developer API).
3. LocalRawFileCollector (For ingesting local CSV/JSON raw feeds from Pakistan sources).
"""

import datetime
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from src.collection.base import BaseCollector

logger = logging.getLogger(__name__)


class RemotiveCollector(BaseCollector):
    """
    Collects tech job listings from Remotive's public API.
    
    API Endpoint: https://remotive.com/api/remote-jobs
    Terms: Free for non-commercial and educational use. Attribution required.
    Limitation Note: Predominantly worldwide remote jobs. Very few direct on-site
    Pakistan listings; eligibility for Pakistan applicants is determined strictly
    by checking whether 'candidate_required_location' is 'Worldwide', 'Anywhere',
    or explicitly includes Pakistan.
    """

    SOURCE_NAME: str = "remotive_api"
    API_URL: str = "https://remotive.com/api/remote-jobs"

    def fetch_raw(
        self,
        category: str = "software-dev",
        search: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        params = {}
        if category:
            params["category"] = category
        if search:
            params["search"] = search
        if limit:
            params["limit"] = limit

        try:
            self._sleep()
            response = self.session.get(self.API_URL, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"[RemotiveCollector] Failed to fetch data: {e}")
            return {}

    def standardize_raw_records(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        jobs = raw_data.get("jobs", [])
        records = []
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        for j in jobs:
            # Preserve original raw values faithfully
            tags = j.get("tags") or []
            skills_raw = "|".join([str(t) for t in tags if t]) if isinstance(tags, list) else str(tags)

            record = {
                "raw_job_id": str(j.get("id", "")),
                "title_raw": j.get("title", ""),
                "company_raw": j.get("company_name", ""),
                "location_raw": j.get("candidate_required_location", ""),
                "candidate_location_raw": j.get("candidate_required_location", ""),
                "category_raw": j.get("category", ""),
                "salary_raw": j.get("salary", ""),
                "job_type_raw": j.get("job_type", ""),
                "skills_raw": skills_raw,
                "description_raw": j.get("description", ""),
                "posting_date_raw": j.get("publication_date", ""),
                "job_url": j.get("url", ""),
                "source": self.SOURCE_NAME,
                "collected_at": now_iso,
            }
            records.append(record)

        return records


class ArbeitnowCollector(BaseCollector):
    """
    Collects tech job listings from Arbeitnow's public job board API.
    
    API Endpoint: https://www.arbeitnow.com/api/job-board-api
    Terms: Free API for developer and aggregator use with source link.
    Limitation Note: Primarily European companies. Remote jobs open worldwide
    or explicitly marked remote can be accessible to Pakistani professionals,
    while on-site roles are based in European cities.
    """

    SOURCE_NAME: str = "arbeitnow_api"
    API_URL: str = "https://www.arbeitnow.com/api/job-board-api"

    def fetch_raw(self, page: int = 1) -> Dict[str, Any]:
        params = {"page": page}
        try:
            self._sleep()
            response = self.session.get(self.API_URL, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"[ArbeitnowCollector] Failed to fetch data: {e}")
            return {}

    def standardize_raw_records(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        jobs = raw_data.get("data", [])
        records = []
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        for j in jobs:
            tags = j.get("tags") or []
            skills_raw = "|".join([str(t) for t in tags if t]) if isinstance(tags, list) else str(tags)
            job_types = j.get("job_types") or []
            job_type_raw = ", ".join(job_types) if isinstance(job_types, list) else str(job_types)

            # Arbeitnow explicitly flags whether a position is remote
            is_remote = j.get("remote", False)
            loc = j.get("location", "")
            location_raw = "Remote" if (is_remote and not loc) else loc
            if is_remote and loc and "remote" not in loc.lower():
                location_raw = f"{loc} (Remote)"

            # Convert unix timestamp to ISO date string if numeric
            created_at = j.get("created_at")
            if isinstance(created_at, (int, float)) and created_at > 0:
                posting_date_raw = datetime.datetime.fromtimestamp(created_at, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
            else:
                posting_date_raw = str(created_at or "")

            record = {
                "raw_job_id": str(j.get("slug", "")),
                "title_raw": j.get("title", ""),
                "company_raw": j.get("company_name", ""),
                "location_raw": location_raw,
                "candidate_location_raw": "Remote" if is_remote else loc,
                "category_raw": None,
                "salary_raw": None,  # Arbeitnow typically does not provide salary numbers
                "job_type_raw": job_type_raw,
                "skills_raw": skills_raw,
                "description_raw": j.get("description", ""),
                "posting_date_raw": posting_date_raw,
                "job_url": j.get("url", ""),
                "source": self.SOURCE_NAME,
                "collected_at": now_iso,
            }
            records.append(record)

        return records


class LocalRawFileCollector(BaseCollector):
    """
    Ingests raw listings from a local raw CSV or JSON file (e.g. from local
    community datasets, open research archives, or verified Pakistan tech dumps).
    """

    SOURCE_NAME: str = "local_feed"

    def __init__(self, file_path: str, output_dir: str = "data/raw"):
        super().__init__(output_dir=output_dir, rate_limit=0.0)
        self.file_path = Path(file_path)

    def fetch_raw(self, **kwargs) -> Any:
        if not self.file_path.exists():
            logger.error(f"[LocalRawFileCollector] File not found: {self.file_path}")
            return []
        
        if self.file_path.suffix.lower() == ".csv":
            df = pd.read_csv(self.file_path)
            return df.to_dict(orient="records")
        elif self.file_path.suffix.lower() == ".json":
            import json
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def standardize_raw_records(self, raw_data: Any) -> List[Dict[str, Any]]:
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        records = []
        if not isinstance(raw_data, list):
            return records

        for row in raw_data:
            records.append({
                "raw_job_id": str(row.get("job_id") or row.get("id") or ""),
                "title_raw": str(row.get("title") or ""),
                "company_raw": str(row.get("company") or ""),
                "location_raw": str(row.get("location") or ""),
                "candidate_location_raw": str(row.get("candidate_location") or row.get("location") or ""),
                "category_raw": str(row.get("category") or ""),
                "salary_raw": str(row.get("salary") or ""),
                "job_type_raw": str(row.get("job_type") or ""),
                "skills_raw": str(row.get("skills") or ""),
                "description_raw": str(row.get("description") or ""),
                "posting_date_raw": str(row.get("posting_date") or ""),
                "job_url": str(row.get("job_url") or ""),
                "source": str(row.get("source") or "local_file"),
                "collected_at": now_iso,
            })
        return records
