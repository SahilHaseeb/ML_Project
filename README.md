# Pakistan AI Job Market Intelligence Platform

> A university data science project analyzing technology job listings in Pakistan.
> Built with Python, Streamlit, Pandas, and Plotly.

![Phase](https://img.shields.io/badge/Phase-2%20of%209-blue)
![Data](https://img.shields.io/badge/Data-Permitted%20APIs%20%26%20Sample-green)
![Python](https://img.shields.io/badge/Python-3.10%2B-green)

---

## 📌 Phase 2 Overview — Data Collection & Cleaning Pipeline

The platform now features a modular data collection and cleaning pipeline:
* **Permitted Sources**: Connects to the Remotive Public API and Arbeitnow Public API with full attribution.
* **Geographic Scope Classification**: Strictly categorizes jobs into `Pakistan (On-site / Hybrid)`, `Pakistan-Eligible (Worldwide Remote)`, `Restricted Remote (Non-Pakistan)`, and `International (On-site)`. Never labels a job as Pakistan-based without evidence.
* **Separation of Raw & Cleaned Data**: Raw snapshots are archived in `data/raw/` as JSON/CSV before cleaning. Cleaned data is stored in `data/processed/cleaned_jobs.csv`.
* **Zero Invention**: Missing salaries, experience requirements, and company details are safely represented as `NaN` / `None`.
* **Sample Fallback**: The Phase 1 synthetic sample dataset (50 jobs) remains fully accessible via the dashboard sidebar selector.

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10 or newer  
- pip (comes with Python)

### 2. Activate virtual environment

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1
```

### 3. Run Job Data Collection & Cleaning Pipeline (Phase 2)

```powershell
# Collect from permitted APIs (Remotive, Arbeitnow) and clean into data/processed/
python src/collection/runner.py --limit 25
```

### 4. Run Unit Tests

```powershell
pytest tests/ -v
```

All 72 unit tests should pass.

### 5. Launch the Streamlit Dashboard

```powershell
streamlit run app.py
```

The app will open at **http://localhost:8501**. You can switch between **Real Cleaned Jobs** and **Phase 1 Sample Data** using the sidebar dropdown.

---

## 📁 Project Structure

```
.
├── app.py                          # Main Streamlit dashboard with dataset switcher
├── pages/                          # Multi-page dashboard
│   ├── 02_job_listings.py         # Browsable table with Geographic Scope filter
│   ├── 03_skills_analysis.py
│   ├── 04_location_analysis.py
│   ├── 05_salary_analysis.py
│   ├── 06_experience_analysis.py
│   ├── 07_historical_trends.py
│   ├── 08_ai_classifier.py         # Placeholder — Phase 6
│   ├── 09_skill_gap.py             # Placeholder — Phase 6
│   └── 10_about.py
├── src/
│   ├── collection/                 # Phase 2: Modular collection pipeline
│   │   ├── base.py                 # BaseCollector (rate-limited, raw archival)
│   │   ├── api_collectors.py       # Remotive & Arbeitnow public API collectors
│   │   ├── pipeline.py             # Collection orchestrator
│   │   └── runner.py               # CLI runner script
│   ├── data_processing/            # Phase 2: Enhanced Pandas cleaning & normalizers
│   │   ├── cleaner.py              # Standardization, deduplication, quality reports
│   │   ├── normalizers.py          # Title, company, salary, experience, location parsers
│   │   └── validators.py           # Schema & numeric range validators
│   ├── analytics/                  # Statistical and KPI calculation modules
│   ├── scraping/                   # Base scraper class
│   ├── database/                   # PostgreSQL integration (Phase 5)
│   └── ml/                         # Machine learning (Phase 6)
├── data/
│   ├── raw/                        # Untouched raw API payloads (JSON & CSV)
│   ├── processed/                  # Cleaned, standardized dataset (cleaned_jobs.csv)
│   └── sample/sample_jobs.csv      # Phase 1 synthetic demo data
├── tests/                          # 72 unit tests (pytest)
│   ├── test_cleaner.py             # Tests for normalizers, parsers, deduplication
│   ├── test_collection.py          # Tests for collectors (mocked responses)
│   ├── test_normalizers.py         # Tests for city/category/skill lookups
│   ├── test_validators.py          # Tests for column & schema validators
│   └── test_analytics.py           # Tests for KPI and chart metrics
├── docs/                           # Schema and data source documentation
└── requirements.txt
```

---

## 🗺️ Development Phases

| Phase | Goal | Status |
|-------|------|--------|
| 1 | Structure + sample data + basic dashboard | ✅ **Done** |
| 2 | Job Data Collection & Data Cleaning Pipeline | ✅ **Done** |
| 3 | EDA & interactive visualizations | 🔜 Next |
| 4 | Approved real-data collection & scraping | 🔜 Planned |
| 5 | PostgreSQL integration | 🔜 Planned |
| 6 | Machine Learning (classifier + skill gap) | 🔜 Planned |
| 7 | NLP & Deep Learning | 🔜 Planned |
| 8 | Full dashboard integration | 🔜 Planned |
| 9 | Testing, docs, GitHub, deployment | 🔜 Planned |

---

## ⚠️ Known Limitations (Phase 1)

- All 50 job listings are **synthetic** — created manually for testing.
- No real web scraping is implemented.
- PostgreSQL is **not** required; the app reads from CSV.
- Machine Learning pages are clearly labeled placeholders.
- Salary and skill statistics are for demonstration only.

---

## 🤝 Contributing

This is a university project. Contributions and feedback are welcome.
Please open an issue before making large changes.

---

## 📜 License

MIT License — see LICENSE file.

---

*Built with ❤️ in Pakistan | Phase 1 of 9*
