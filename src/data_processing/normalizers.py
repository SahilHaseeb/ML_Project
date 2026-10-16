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
from typing import Optional, Tuple
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


# ─── Canonical Pakistan Cities ───────────────────────────────────────────────
PAKISTAN_CITIES = {
    "Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad",
    "Multan", "Peshawar", "Quetta", "Sialkot", "Hyderabad",
    "Gujranwala", "Abbottabad"
}


def classify_location_scope(location: str, candidate_required_location: str = "") -> str:
    """
    Classifies the geographic scope of a job listing.

    Strict Rule: Never label a job as Pakistan-based without evidence from
    its location or source data.

    Returns one of:
      - 'Pakistan (On-site / Hybrid)'
      - 'Pakistan (Remote / Hybrid)'
      - 'Pakistan-Eligible (Worldwide Remote)'
      - 'Restricted Remote (Non-Pakistan)'
      - 'International (On-site)'
      - 'Unspecified'
    """
    loc_clean = str(location or "").strip()
    cand_clean = str(candidate_required_location or "").strip()

    loc_lower = loc_clean.lower()
    cand_lower = cand_clean.lower()

    # 1. Direct Pakistan physical locations
    norm_city = normalize_city(loc_clean)
    if norm_city in PAKISTAN_CITIES or "pakistan" in loc_lower or "pakistan" in cand_lower:
        if "remote" in loc_lower or "remote" in cand_lower:
            return "Pakistan (Remote / Hybrid)"
        return "Pakistan (On-site / Hybrid)"

    # 2. Worldwide remote jobs (eligible for Pakistan candidates)
    worldwide_terms = [
        "worldwide", "anywhere", "global", "all countries", "work from anywhere",
        "remote (worldwide)", "worldwide (remote)", "remote - worldwide"
    ]
    if any(term in cand_lower for term in worldwide_terms) or any(term in loc_lower for term in worldwide_terms):
        return "Pakistan-Eligible (Worldwide Remote)"

    # 3. If remote is mentioned, check if restricted to non-Pakistan region
    is_remote = "remote" in loc_lower or "remote" in cand_lower
    restricted_regions = [
        "usa", "us only", "united states", "europe", "eu only", "emea",
        "uk only", "united kingdom", "canada", "germany", "france", "latam",
        "north america", "apac only"
    ]
    if is_remote and (any(region in cand_lower for region in restricted_regions) or any(region in loc_lower for region in restricted_regions)):
        return "Restricted Remote (Non-Pakistan)"

    # 4. If remote is explicitly stated without region restriction
    if is_remote:
        return "Pakistan-Eligible (Worldwide Remote)"

    # 5. International physical location
    if loc_clean and loc_clean.lower() not in ["", "none", "nan", "unknown"]:
        return "International (On-site)"

    return "Unspecified"


def clean_job_title(title: str) -> str:
    """
    Cleans raw job title:
    - Strips bracketed text like [Remote], (Remote), (m/f/d), etc.
    - Strips hiring tags like 'Urgent:', 'Immediate:', etc.
    - Preserves standard role names.
    """
    if not isinstance(title, str) or not title.strip():
        return ""
    
    t = title.strip()
    # Strip bracketed metadata
    t = re.sub(r"\[.*?\]", "", t)
    t = re.sub(r"\((?:m/f/d|f/m/d|w/m/d|remote|hybrid|h/f)\)", "", t, flags=re.IGNORECASE)
    # Strip common recruitment prefix tags
    t = re.sub(r"^(?:hiring|urgent|we are hiring|immediate requirement|open role)[:\s\-]+", "", t, flags=re.IGNORECASE)
    # Clean whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t


def clean_company_name(company: str) -> str:
    """
    Normalizes company names by trimming trailing corporate suffixes.
    Never invents a missing company name.
    """
    if not isinstance(company, str) or not company.strip():
        return ""

    c = company.strip()
    # Strip corporate endings (including standalone limited)
    c = re.sub(
        r"[\s,]+(?:pvt\.?\s*ltd\.?|private\s*limited|limited|ltd\.?|inc\.?|llc|corp\.?|corporation|gmbh)$",
        "",
        c,
        flags=re.IGNORECASE,
    ).strip()
    # Strip trailing punctuation
    c = c.rstrip("-,. ")
    return c if c else company.strip()


def parse_experience_years(text: str) -> tuple[Optional[float], Optional[float]]:
    """
    Extracts experience_min and experience_max from free text.
    Returns (None, None) if unknown — never invents numbers.
    """
    if not isinstance(text, str) or not text.strip():
        return None, None

    t = text.lower().strip()

    # Fresh / Entry level
    if re.search(r"\b(fresh|entry\s*level|intern|internship|graduate)\b", t):
        return 0.0, 1.0

    # Range pattern: e.g. "3-5 years", "2 to 4 yrs"
    range_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?|\+)", t)
    if range_match:
        try:
            exp_min = float(range_match.group(1))
            exp_max = float(range_match.group(2))
            if exp_min <= exp_max:
                return exp_min, exp_max
        except ValueError:
            pass

    # Minimum pattern: e.g. "3+ years", "min 2 years", "at least 5 years"
    min_match = re.search(r"(?:min(?:imum)?|at\s*least)?\s*(\d+(?:\.\d+)?)\s*(?:\+|years?|yrs?)", t)
    if min_match:
        try:
            exp_min = float(min_match.group(1))
            return exp_min, None
        except ValueError:
            pass

    return None, None


def parse_salary(salary_raw: str) -> tuple[Optional[float], Optional[float], Optional[str]]:
    """
    Safely parses salary string into (salary_min, salary_max, currency).
    Returns (None, None, None) if undisclosed or unparseable.
    Never estimates or guesses salary.
    """
    if not isinstance(salary_raw, str) or not salary_raw.strip():
        return None, None, None

    s = salary_raw.strip().lower()

    # Skip non-numeric / undisclosed values
    undisclosed = ["confidential", "undisclosed", "competitive", "market competitive", "negotiable", "tbd", "n/a"]
    if any(u in s for u in undisclosed):
        return None, None, None

    # Detect currency
    currency = None
    if "pkr" in s or "rs" in s or "rupee" in s:
        currency = "PKR"
    elif "$" in s or "usd" in s:
        currency = "USD"
    elif "€" in s or "eur" in s:
        currency = "EUR"
    elif "£" in s or "gbp" in s:
        currency = "GBP"

    # Multiplier handling: 'k' -> 1,000, 'lac'/'lakh' -> 100,000
    def _parse_val(val_str: str) -> Optional[float]:
        v = val_str.strip().replace(",", "")
        mult = 1.0
        if "k" in v:
            mult = 1000.0
            v = v.replace("k", "")
        elif "lac" in v or "lakh" in v:
            mult = 100000.0
            v = re.sub(r"lacs?|lakhs?", "", v)
        try:
            return round(float(v) * mult, 2)
        except ValueError:
            return None

    # Strip currency signs before searching numbers
    clean_s = s.replace("$", "").replace("€", "").replace("£", "")
    clean_s = re.sub(r"\b(?:usd|eur|gbp|pkr|rs|rupees?)\b", "", clean_s)

    # Check for range: e.g. "100,000 - 130,000" or "150k - 250k" or "1.5 lac - 2.5 lac"
    range_match = re.search(r"(\d[\d,]*(?:\.\d+)?\s*(?:k|lac|lakh)?)\s*(?:-|to)\s*(\d[\d,]*(?:\.\d+)?\s*(?:k|lac|lakh)?)", clean_s)
    if range_match:
        min_v = _parse_val(range_match.group(1))
        max_v = _parse_val(range_match.group(2))
        if min_v and max_v:
            if min_v > max_v:
                min_v, max_v = max_v, min_v
            return min_v, max_v, currency

    # Single number
    single_match = re.search(r"(\d[\d,]*(?:\.\d+)?\s*(?:k|lac|lakh)?)", clean_s)
    if single_match:
        val = _parse_val(single_match.group(1))
        if val and val > 0:
            return val, None, currency

    return None, None, currency


def infer_category(title: str, skills: str = "", default: str = "Software Development") -> str:
    """
    Infers technological category from title and skills if category is missing in raw source.
    """
    text = f"{title} {skills}".lower()

    if any(k in text for k in ["data science", "data scientist", "machine learning", "deep learning", "ai engineer", "nlp"]):
        return "Data Science"
    if any(k in text for k in ["data analyst", "data analytics", "business intelligence", "bi analyst", "tableau", "power bi"]):
        return "Data Analytics"
    if any(k in text for k in ["data engineer", "data engineering", "etl", "spark", "hadoop", "airflow"]):
        return "Data Engineering"
    if any(k in text for k in ["devops", "cloud", "aws", "kubernetes", "docker", "sre", "infrastructure"]):
        return "DevOps"
    if any(k in text for k in ["frontend", "front-end", "react", "vue", "angular", "css", "html"]):
        return "Web Development"
    if any(k in text for k in ["backend", "back-end", "django", "flask", "fastapi", "spring", "laravel", "node", "express"]):
        return "Software Development"
    if any(k in text for k in ["full stack", "fullstack", "web developer"]):
        return "Web Development"
    if any(k in text for k in ["qa", "quality assurance", "test engineer", "automation engineer", "tester"]):
        return "Quality Assurance"
    if any(k in text for k in ["ui/ux", "product designer", "ui designer", "ux designer"]):
        return "UI/UX Design"
    if any(k in text for k in ["cybersecurity", "security analyst", "infosec", "penetration tester"]):
        return "Cybersecurity"
    if any(k in text for k in ["mobile developer", "android", "ios", "flutter", "react native"]):
        return "Mobile Development"

    return default

