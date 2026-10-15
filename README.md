# Pakistan AI Job Market Intelligence Platform

> A university data science project analyzing technology job listings in Pakistan.
> Built with Python, Streamlit, Pandas, and Plotly.

![Phase](https://img.shields.io/badge/Phase-1%20of%209-blue)
![Data](https://img.shields.io/badge/Data-Sample%20Only-orange)
![Python](https://img.shields.io/badge/Python-3.10%2B-green)

---

## ⚠️ Important Notice

This platform currently uses **50 synthetic sample job listings** for demonstration purposes.
It does **not** represent the real Pakistan job market.
Real data collection begins in **Phase 4** after data source permissions are confirmed.

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10 or newer  
- pip (comes with Python)
- Git (optional, for version control)

### 2. Clone the repository (or open the folder)

```bash
# If using Git:
git clone <your-repo-url>
cd "pakistan-ai-jobs"

# Or just open the folder:
cd "e:\ML Project"
```

### 3. Create and activate a virtual environment

```powershell
# Create the environment
python -m venv venv

# Activate it (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# You should see (venv) at the start of your prompt
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Set up environment variables (optional for Phase 1)

```powershell
# Copy the template
copy .env.example .env

# Edit .env if you want to configure PostgreSQL (not required for Phase 1)
```

### 6. Launch the application

```powershell
streamlit run app.py
```

The app will open in your browser at **http://localhost:8501**

---

## 🧪 Running Tests

```powershell
pytest tests/ -v
```

Expected output: all tests should pass.

---

## 📁 Project Structure

```
.
├── app.py                          # Main Streamlit entry point
├── pages/                          # One file per dashboard page
│   ├── 02_job_listings.py
│   ├── 03_skills_analysis.py
│   ├── 04_location_analysis.py
│   ├── 05_salary_analysis.py
│   ├── 06_experience_analysis.py
│   ├── 07_historical_trends.py
│   ├── 08_ai_classifier.py         # Placeholder
│   ├── 09_skill_gap.py             # Placeholder
│   └── 10_about.py
├── src/
│   ├── data_processing/            # Cleaning, validation, normalization
│   ├── analytics/                  # Pure analysis functions
│   ├── scraping/                   # Web scraper base class
│   ├── database/                   # PostgreSQL integration (Phase 5)
│   └── ml/                         # Machine learning (Phase 6)
├── data/
│   └── sample/sample_jobs.csv      # Synthetic demo data
├── tests/                          # pytest unit tests
├── docs/                           # Documentation
├── requirements.txt
├── .env.example
└── README.md
```

---

## 📊 Dashboard Pages

| Page | Description |
|------|-------------|
| 🏠 Home / Overview | KPI cards + top categories + top skills + city distribution |
| 💼 Job Listings | Searchable, filterable table of all listings with detail view |
| 🔧 Skills Analysis | Top skills bar chart, per-category skills, heatmap |
| 📍 Location Analysis | City bar chart, remote vs on-site, category-by-city |
| 💰 Salary Analysis | Coverage rate, category medians, salary distribution |
| 📈 Experience Analysis | Level distribution, avg experience by category, scatter |
| 📅 Historical Trends | Monthly volume, category trend lines, skill growth |
| 🧠 AI Classifier | Placeholder — Phase 6 |
| 🎯 Skill Gap Analyzer | Placeholder — Phase 6 |
| ℹ️ About | Data sources, limitations, tech stack, ethics |

---

## 🗺️ Development Phases

| Phase | Goal | Status |
|-------|------|--------|
| 1 | Structure + sample data + basic dashboard | ✅ **Done** |
| 2 | Data validation & cleaning pipeline | 🔜 Next |
| 3 | EDA & interactive visualizations | 🔜 Planned |
| 4 | Approved real-data collection | 🔜 Planned |
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
