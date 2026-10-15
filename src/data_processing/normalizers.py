"""
src/data_processing/normalizers.py
------------------------------------
Standardises free-text values in the job data so that analysis
functions can count them reliably.

Example problem this solves:
  "Lahore" / "lahore" / "LHR" / "Lahore, Pakistan"
  → all become the single canonical string "Lahore"
"""

import re
import logging
import pandas as pd

logger = logging.getLogger(__name__)

# ─── City aliases → canonical name ────────────────────────────────────────────
CITY_MAP = {
    # Karachi
    "karachi": "Karachi", "khi": "Karachi", "karāchi": "Karachi",
    # Lahore
    "lahore": "Lahore", "lhr": "Lahore", "lahor": "Lahore",
    # Islamabad
    "islamabad": "Islamabad", "isb": "Islamabad",
    # Rawalpindi
    "rawalpindi": "Rawalpindi", "rwp": "Rawalpindi", "pindi": "Rawalpindi",
    # Other major cities
    "faisalabad": "Faisalabad", "fsd": "Faisalabad",
    "multan": "Multan", "mux": "Multan",
    "peshawar": "Peshawar", "pew": "Peshawar",
    "quetta": "Quetta", "uet": "Quetta",
    "sialkot": "Sialkot",
    "hyderabad": "Hyderabad",
    "gujranwala": "Gujranwala",
    "abbottabad": "Abbottabad",
    # Remote / hybrid patterns
    "remote": "Remote", "work from home": "Remote", "wfh": "Remote",
    "hybrid": "Hybrid",
}

# ─── Category aliases → canonical name ────────────────────────────────────────
CATEGORY_MAP = {
    "software development": "Software Development",
    "software engineering": "Software Development",
    "backend": "Software Development",
    "backend development": "Software Development",
    "frontend": "Web Development",
    "frontend development": "Web Development",
    "web development": "Web Development",
    "full stack": "Web Development",
    "data science": "Data Science",
    "data scientist": "Data Science",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "ai": "NLP / AI",
    "nlp": "NLP / AI",
    "nlp / ai": "NLP / AI",
    "artificial intelligence": "NLP / AI",
    "data analytics": "Data Analytics",
    "data analysis": "Data Analytics",
    "business intelligence": "Data Analytics",
    "data engineering": "Data Engineering",
    "devops": "DevOps",
    "cloud engineering": "Cloud Engineering",
    "cloud": "Cloud Engineering",
    "mobile development": "Mobile Development",
    "mobile": "Mobile Development",
    "cybersecurity": "Cybersecurity",
    "security": "Cybersecurity",
    "database": "Database",
    "dba": "Database",
    "networking": "Networking",
    "embedded systems": "Embedded Systems",
    "blockchain": "Blockchain",
    "ui/ux design": "UI/UX Design",
    "ux": "UI/UX Design",
    "erp / sap": "ERP / SAP",
    "sap": "ERP / SAP",
    "crm / salesforce": "CRM / Salesforce",
    "salesforce": "CRM / Salesforce",
    "quality assurance": "Quality Assurance",
    "qa": "Quality Assurance",
    "testing": "Quality Assurance",
    "project management": "Project Management",
    "product management": "Product Management",
}

# ─── Common skill aliases → canonical name ────────────────────────────────────
SKILL_MAP = {
    "python3": "Python",
    "py": "Python",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "react.js": "React",
    "reactjs": "React",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "pytorch": "PyTorch",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "scikit learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "scikit-learn": "Scikit-learn",
    "rest api": "REST API",
    "restful api": "REST API",
    "api": "REST API",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "cv": "Computer Vision",
    "computer vision": "Computer Vision",
}


def _lookup(value: str, mapping: dict, label: str) -> str:
    """Internal: try to find a canonical name, return original if not found."""
    if not isinstance(value, str):
        return value
    cleaned = value.strip().lower()
    # Try exact match first
    if cleaned in mapping:
        return mapping[cleaned]
    # Try to find a partial city match for compound location strings
    # e.g. "Lahore, Punjab" → "Lahore"
    for key, canonical in mapping.items():
        if key in cleaned:
            return canonical
    return value.strip()  # Return original (stripped) if no match


def normalize_city(location: str) -> str:
    """Map a raw location string to a canonical city name."""
    return _lookup(location, CITY_MAP, "city")


def normalize_category(category: str) -> str:
    """Map a raw category string to a canonical category name."""
    return _lookup(category, CATEGORY_MAP, "category")


def normalize_skill(skill: str) -> str:
    """Map a raw skill string to a canonical skill name."""
    if not isinstance(skill, str):
        return skill
    cleaned = skill.strip().lower()
    return SKILL_MAP.get(cleaned, skill.strip())


def normalize_skills_column(df: pd.DataFrame, col: str = "skills") -> pd.DataFrame:
    """
    The 'skills' column stores pipe-separated skill names like:
        "Python|Django|REST API"
    
    This function:
    1. Splits each row's skills by "|"
    2. Normalizes each individual skill name
    3. Joins them back with "|"
    """
    if col not in df.columns:
        return df

    def _normalize_row(value):
        if pd.isna(value):
            return value
        skills = [s.strip() for s in str(value).split("|") if s.strip()]
        normalized = [normalize_skill(s) for s in skills]
        return "|".join(normalized)

    df[col] = df[col].apply(_normalize_row)
    return df


def normalize_location_column(df: pd.DataFrame, col: str = "location") -> pd.DataFrame:
    """Apply city normalization to every row in the location column."""
    if col not in df.columns:
        return df
    df[col] = df[col].apply(
        lambda x: normalize_city(x) if isinstance(x, str) else x
    )
    return df


def normalize_category_column(df: pd.DataFrame, col: str = "category") -> pd.DataFrame:
    """Apply category normalization to every row in the category column."""
    if col not in df.columns:
        return df
    df[col] = df[col].apply(
        lambda x: normalize_category(x) if isinstance(x, str) else x
    )
    return df
