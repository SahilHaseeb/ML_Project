# PakSkillIQ — Project Master Log & Progress Tracker
**Project**: Pakistan AI Job Market Intelligence Platform  
**Repository**: [https://github.com/SahilHaseeb/ML_Project](https://github.com/SahilHaseeb/ML_Project)  
**Live Application**: [https://pakskilliq.onrender.com/](https://pakskilliq.onrender.com/)  
**Created**: 2026-10-16  
**Last Updated**: 2026-10-16  

---

## 1. Project Overview & Architecture

### 1.1 Purpose & Mission
PakSkillIQ is a data intelligence platform built to monitor, analyze, and present job market trends for technology, Artificial Intelligence (AI), Machine Learning (ML), and Data Science roles relevant to Pakistani students, fresh graduates, and software engineers. It highlights:
- In-demand technical skills and toolsets.
- Geographic distribution across major Pakistani tech hubs (Lahore, Karachi, Islamabad, etc.) vs. worldwide remote roles.
- Salary transparency, currency breakdowns (PKR / USD / EUR), and compensation ranges.
- Experience level distributions (Fresh / Junior / Mid / Senior / Lead).
- Historical hiring trends and monthly posting cadence.

### 1.2 Technology Stack
- **Core Language**: Python 3.12
- **Web Dashboard**: Streamlit 1.66 (multi-page architecture with custom dark tech styling)
- **Data Manipulation**: Pandas 3.0.6, NumPy
- **Visualizations**: Plotly Express & Plotly Graph Objects
- **Testing**: Pytest 9.1.1
- **HTTP / APIs**: Requests 2.32
- **Deployment**: Render Web Service (connected to GitHub `main` branch, auto-deploying via `streamlit run app.py`)

---

## 2. Phase-by-Phase Roadmap & Status

| Phase | Title | Status | Summary |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Interactive Web Dashboard & Analytics | **COMPLETED** | 10 multi-page Streamlit views, dark UI, 50 sample records, comprehensive test suite. |
| **Phase 2** | Job Data Collection & Data Cleaning | **COMPLETED** | Modular collectors (Remotive, Arbeitnow), cleaning pipeline, 314 real records; live on GitHub (`205df6d`). |
| **Phase 3** | Pipeline Automation & Historical Data | **IN-PROGRESS** | Step 3.1 & 3.2 complete (incremental merge engine, GitHub Actions workflow created, 88 tests passing); Step 3.3 (manual run) pending. |
| **Phase 4** | Machine Learning & NLP Modeling | **PLANNED** | TF-IDF / transformer job category classifier, resume-to-job skill gap scoring. |
| **Phase 5** | Production Hardening & Monitoring | **PLANNED** | Persistent DB (PostgreSQL / BigQuery), automated alerting, health metrics. |

---

## 3. Detailed Phase Accomplishments

### Phase 1: Dashboard & Sample Dataset (Completed)
- **Multi-Page Dashboard**:
  - `app.py`: Overview page with high-level KPI cards, dataset switcher, quality reports.
  - `pages/02_job_listings.py`: Filterable data table by city, skill, role, remote status.
  - `pages/03_skills_analysis.py`: Frequency charts of top programming languages and frameworks.
  - `pages/04_location_analysis.py`: Job counts across Pakistani cities vs. remote.
  - `pages/05_salary_analysis.py`: Salary distributions and disclosure rate analytics.
  - `pages/06_experience_analysis.py`: Categorization into Fresh, Junior, Mid, Senior, Lead.
  - `pages/07_historical_trends.py`: Monthly posting timelines.
  - `pages/08_ai_classifier.py`: UI demonstration placeholder for ML classification.
  - `pages/09_skill_gap.py`: UI demonstration placeholder for resume skill gap analysis.
  - `pages/10_about.py`: Methodology, ethics, and API documentation.
- **Sample Dataset**:
  - `data/sample/sample_jobs.csv`: 50 synthetic records reflecting typical Pakistani tech listings.
- **Analytics Modules**:
  - `src/analytics/` (`overview.py`, `skills.py`, `locations.py`, `salaries.py`, `experience.py`, `trends.py`).

### Phase 2: Data Collection & Cleaning (Active)
- **Modular Ingestion Pipeline** (`src/collection/`):
  - `base.py`: Abstract `BaseCollector` interface with standardized schemas.
  - `remotive.py`: Collector for Remotive Public API (remote tech roles).
  - `arbeitnow.py`: Collector for Arbeitnow Public API (European & global remote tech roles).
  - `runner.py`: Orchestrator that queries APIs, stores raw data in `data/raw/`, and triggers cleaning.
- **Cleaning & Standardization Engine** (`src/data_processing/`):
  - `cleaner.py`: Standardizes titles, companies, salary parsing, experience extraction, and location scope tagging.
  - `normalizers.py`: Normalizes city names, categories, and technical skill tags.
  - `validators.py`: Verifies mandatory schema columns, parses dates, and outputs data quality metrics.
  - **Location Scope Policy**: Strictly separates `pakistan_based` (physically in Pakistan), `pakistan_eligible` (worldwide remote), and `international_only` (restricted to US/EU/other countries).
- **Generated Data**:
  - `data/processed/cleaned_jobs.csv`: 314 cleaned records (300 Arbeitnow, 14 Remotive). File size: 2.35 MB.
  - `data/raw/`: Raw JSON API responses and aggregated uncleaned CSVs.
- **Test Suite**:
  - 72 unit tests across `tests/test_analytics.py`, `tests/test_cleaner.py`, `tests/test_collection.py`, `tests/test_normalizers.py`, and `tests/test_validators.py`. 100% passing.

---

## 4. Current Deployment & Infrastructure Status

### Render Deployment Behavior
- **Recent Update (2026-10-16)**:
  - Commit `205df6d` (`feat: add cleaned jobs dataset and update gitignore`) was committed and pushed to GitHub `origin/main` by the user.
  - `data/processed/cleaned_jobs.csv` is now tracked in GitHub.
  - Render pulls from GitHub `main`. During build and app boot, `app.py` checks `os.path.exists("data/processed/cleaned_jobs.csv")`. Now finding the 314 cleaned jobs file present, the live dashboard exposes and activates `"🌐 Real Cleaned Jobs (Phase 2)"` alongside the sample data option.

---

## 5. Architectural Decisions, Constraints & Limitations

1. **Strict Data Authenticity**: Never fabricate missing salaries, company names, or skills. If undisclosed by the employer, values must remain null (`None` / `NaN`).
2. **Location Classification Integrity**: Never label an overseas job as "Pakistan-based" without explicit evidence in the job post.
3. **API Limitations**: Public APIs like Remotive and Arbeitnow predominantly list US and European tech roles. While they offer valuable worldwide remote listings accessible to Pakistani engineers, physical on-site Pakistani job postings in these APIs are rare.
4. **Preservation of Dual Datasets**: The 50-job sample dataset must always remain available in the sidebar selector for testing and demonstrations even after real data is loaded.
5. **Separation of Concerns**: Raw payloads (`data/raw/`) must never be modified directly or committed to Git. Cleaning is executed idempotently via `src/data_processing/cleaner.py`.

---

## 6. Current Task & Immediate Next Steps

### Current Task Status
- **Phase 3 Pre-Commit Review Completed & Verified**:
  - Ran `git status --short`; confirmed branch `main` and remote `origin`.
  - Audited `.github/workflows/scheduled_collection.yml`. Discovered a potential Git rebase conflict where `git pull --rebase` was sequenced before `git commit`; corrected sequence so commit occurs first.
  - Inspected all code diffs (`cleaner.py`, `pipeline.py`, `runner.py`, `test_incremental_merge.py`, `scheduled_collection.yml`).
  - Verified runner CLI arguments (`--limit`) match workflow parameters.
  - Confirmed triple-layer anti-overwrite protections (early return on empty collection, safe merge, and shrink detection).
  - Confirmed working tree purity (no secrets, raw snapshots, or temporary files).
  - Executed offline unit tests (all 88 passed).
  - Production dataset `cleaned_jobs.csv` verified unchanged (314 records).

### Remaining Phase 3 Steps
1. **User Review & Publishing**:
   - Review pre-commit review report.
   - Stage and commit Phase 3 implementation files:
     - `.github/workflows/scheduled_collection.yml`
     - `src/data_processing/cleaner.py`
     - `src/collection/pipeline.py`
     - `src/collection/runner.py`
     - `tests/test_incremental_merge.py`
     - `PROJECT_MASTER_LOG.md`
   - Push to GitHub `origin/main`.
2. **Step 3.3: Manual Verification via GitHub Actions Tab**:
   - Verify workflow permissions ("Read and write permissions" enabled under repo Settings -> Actions -> General).
   - Trigger manual run of "Scheduled Job Collection" workflow via GitHub Actions tab.
   - Verify execution log and auto-deploy on Render.

---

## 7. Chronological Task Log

### Task 1: 2026-10-16 — Phase 2 Review, Verification & Safe .gitignore Adjustment
- **User Request**: Inspect `.gitignore` and `app.py`, safely adjust `.gitignore` to track `data/processed/cleaned_jobs.csv` without including `data/raw/`, verify fallback, run tests, and provide exact Git commands without committing or pushing.
- **Completed**:
  - Inspected `.gitignore` and `app.py`.
  - Confirmed `cleaned_jobs.csv` has 314 rows and 2.35 MB size.
  - Verified `app._load_dataset_cached()` fallback to 50 sample rows.
  - Updated `.gitignore` (`data/processed/*` + `!data/processed/cleaned_jobs.csv`).
  - Executed pytest suite: 72 passed in 4.22s.
- **Files Modified**: `.gitignore`
- **Commands Executed**:
  - `Get-ChildItem -Recurse data` (verified file paths and sizes)
  - `python -c "import pandas as pd; ..."` (verified 314 rows: 300 Arbeitnow, 14 Remotive)
  - `python -c "import app; ..."` (verified fallback to 50 sample rows when real CSV is missing)
  - `git check-ignore ...` (verified raw data remains excluded while cleaned CSV is unignored)
  - `pytest tests/ -v` (72 passed)
- **Git & Deployment Outcome**:
  - User reviewed git status and executed the provided commands.
  - Commit `205df6d` (`feat: add cleaned jobs dataset and update gitignore`) successfully pushed to GitHub `origin/main`.

### Task 2: 2026-10-16 — Establishment of Project Master Log & Antigravity Rule System
- **User Request**:
  - Create `PROJECT_MASTER_LOG.md` in repository root documenting complete project history, phases, decisions, and status.
  - Configure a persistent Antigravity project rule to maintain this log automatically after every future task.
  - Commit and push only the documentation and rule files to GitHub using commit message `docs: add persistent project progress log`.
- **Completed**:
  - Generated `PROJECT_MASTER_LOG.md` in project root with full history, metrics, and architecture.
  - Established persistent Antigravity rules in `AGENTS.md` and `.agents/rules/project_master_log.md`.
  - Inspected Git status and staged only the authorized documentation/rule files.
  - Committed and pushed documentation files to GitHub `origin/main` (commit `6f90c56`).
- **Files Created**:
  - `PROJECT_MASTER_LOG.md`
  - `AGENTS.md`
  - `.agents/rules/project_master_log.md`
- **Commands Executed**:
  - `git status`, `git branch`, `git remote -v`
  - `git log -n 5 --oneline` (verified `205df6d`)
  - `git add PROJECT_MASTER_LOG.md AGENTS.md .agents/`
  - `git commit -m "docs: add persistent project progress log"`
  - `git push origin main` (pushed commit `6f90c56`)
- **Git Status**: Pushed to GitHub `origin/main`.

### Task 3: 2026-10-16 — Phase 3 Automation Planning & Pipeline Architecture Inspection
- **User Request**:
  - Inspect Phase 2 collection entry point, API mechanisms, dataset saving, deduplication, Render data loading, and current Git status.
  - Explain a safe design for scheduled job collection via GitHub Actions and how data reaches Render.
  - Do not modify code files, run APIs, regenerate datasets, commit, push, or deploy.
  - Identify risks, required secrets, scheduling options, and next steps.
  - Update `PROJECT_MASTER_LOG.md` with inspection findings and plan.
- **Completed**:
  - Inspected `src/collection/runner.py`, `src/collection/pipeline.py`, `src/collection/api_collectors.py`, `src/collection/base.py`, `src/data_processing/cleaner.py`, and `app.py`.
  - Verified Git branch `main` is clean and in sync with `origin/main`.
  - Identified critical risk: current `save_cleaned_data()` overwrites rather than appends; designed incremental merge solution.
  - Formulated GitHub Actions workflow architecture (`contents: write`, conditional commits, weekly cron + manual dispatch).
  - Documented findings, risks, and roadmap in `PROJECT_MASTER_LOG.md`.
- **Files Inspected**:
  - `PROJECT_MASTER_LOG.md`
  - `src/collection/runner.py`
  - `src/collection/pipeline.py`
  - `src/collection/api_collectors.py`
  - `src/collection/base.py`
  - `src/data_processing/cleaner.py`
  - `app.py`
- **Files Modified**:
  - `PROJECT_MASTER_LOG.md`
- **Commands Executed**:
  - `git status; git branch`
- **Git Status**: Local documentation update only.

### Task 4: 2026-10-16 — Phase 3 Step 3.1: Safe Incremental Merging Implementation
- **User Request**:
  - Implement safe incremental merging for the job collection pipeline.
  - Preserve all existing records in `data/processed/cleaned_jobs.csv`.
  - Deduplicate combined dataset using existing fingerprint logic.
  - Never overwrite existing dataset with an empty or incomplete result on API failure.
  - Add offline unit tests for merging, deduplication, preservation, and failure modes.
  - Do not create GitHub Actions workflow yet, and do not commit or push.
- **Completed**:
  - Added `merge_cleaned_datasets()` and `safe_incremental_save()` to `src/data_processing/cleaner.py` with dataset shrink protection (`ValueError` on shrink) and atomic writing (`.tmp` file + `os.replace`).
  - Updated `src/collection/pipeline.py` with try/except error isolation per collector.
  - Updated `src/collection/runner.py` with `run_collection()`, safe preservation when APIs fail or return 0 records, and `--no-merge` CLI argument.
  - Created `tests/test_incremental_merge.py` with 16 comprehensive offline unit tests.
  - Executed full test suite: 88 passed (16 new + 72 previous), 0 failures.
  - Verified production dataset `data/processed/cleaned_jobs.csv` integrity: 314 rows, SHA256 checksum unchanged.
- **Files Modified**:
  - `src/data_processing/cleaner.py`
  - `src/collection/pipeline.py`
  - `src/collection/runner.py`
  - `PROJECT_MASTER_LOG.md`
- **Files Created**:
  - `tests/test_incremental_merge.py`
- **Commands Executed**:
  - `python -c "import pandas as pd; ..."` (verified 314 rows and SHA256 before edits)
  - `pytest tests/test_incremental_merge.py -v` (16 passed in 3.76s)
  - `pytest tests/ -v` (88 passed in 3.99s)
  - `python -c "import pandas as pd; ..."` (verified 314 rows and SHA256 after edits)
  - `git status`
- **Git Status**: Local modifications only (not staged, not committed, not pushed).

### Task 5: 2026-10-16 — Phase 3 Step 3.2: GitHub Actions Scheduled Collection Workflow
- **User Request**:
  - Create `.github/workflows/scheduled_collection.yml` with weekly schedule (`0 6 * * 1`) and manual `workflow_dispatch`.
  - Python 3.12, pre-flight test gate, incremental merge, concurrency protection, least-privilege `contents: write`.
  - Conditional commit/push of `data/processed/cleaned_jobs.csv` only on genuine changes.
  - Safe rebase, no force-push, no live API execution during task.
  - Do not commit or push yet; update `PROJECT_MASTER_LOG.md`.
- **Completed**:
  - Inspected repository configuration, CLI arguments, and dependencies in `requirements.txt`.
  - Authored `.github/workflows/scheduled_collection.yml` matching all safety, concurrency, and permission constraints.
  - Conducted offline workflow validation (syntax, triggers, inputs, actions, step chaining).
  - Executed complete unit test suite: 88 passed in 3.86s.
  - Verified `data/processed/cleaned_jobs.csv` integrity: 314 records, SHA256 checksum untouched.
- **Files Created**:
  - `.github/workflows/scheduled_collection.yml`
- **Files Modified**:
  - `PROJECT_MASTER_LOG.md`
- **Commands Executed**:
  - `pytest tests/ -v` (88 passed)
  - `python -c "import pandas as pd; ..."` (checksum and row count verification)
  - `git status`
- **Git Status**: Local files ready for user review (unstaged, uncommitted).

### Task 6: 2026-10-16 — Pre-Commit Review & Verification for Phase 3
- **User Request**:
  - Run `git status --short`, confirm branch and remote.
  - Perform thorough audit of `.github/workflows/scheduled_collection.yml` (commands, YAML, permissions, dependencies, arguments, rebase/push).
  - Inspect diffs for all Phase 3 files.
  - Verify CLI argument compatibility and failure protections.
  - Verify working tree purity (no secrets, raw snapshots, temporary files).
  - Run safe offline validation and tests; report defects or confirm readiness.
- **Completed**:
  - Confirmed Git status: 4 modified tracked files (`PROJECT_MASTER_LOG.md`, `pipeline.py`, `runner.py`, `cleaner.py`), 2 untracked items (`.github/`, `tests/test_incremental_merge.py`). Branch `main` on `origin`.
  - Discovered and fixed defect in `.github/workflows/scheduled_collection.yml`: corrected git command sequence so `git commit` executes before `git pull --rebase origin main` (preventing exit code 128 "index contains uncommitted changes").
  - Inspected diffs for all 5 Phase 3 code/doc files. Confirmed strict compliance with canonical schema and location classification.
  - Verified argument consistency: `--limit` cleanly maps to `runner.py`'s argparse.
  - Confirmed triple-layer anti-overwrite protection: `runner.py` early exit + `safe_incremental_save()` empty batch rejection + dataset shrink check.
  - Confirmed working tree cleanliness: no `.env`, no credentials, `data/raw/` remains excluded by `.gitignore`.
  - Executed test suite: 88 passed in 10.56s.
  - Verified production dataset `cleaned_jobs.csv`: exactly 314 rows, SHA256 checksum `efb248430acbcf250bd215b32c054cd61927b943125367b635de192de70d78c0` (100% verified untouched).
- **Files Modified**:
  - `.github/workflows/scheduled_collection.yml` (fixed rebase command ordering)
  - `PROJECT_MASTER_LOG.md` (updated status and added review log)
- **Commands Executed**:
  - `git status --short; git branch; git remote -v`
  - Python simulated git rebase script (reproduced exit code 128 and verified fix)
  - `git diff src/data_processing/cleaner.py`
  - `git diff src/collection/pipeline.py`
  - `git diff src/collection/runner.py`
  - `git diff PROJECT_MASTER_LOG.md`
  - `pytest tests/ -q` (88 passed)
  - `python -c "import pandas as pd; ..."` (production dataset hash check)
- **Git Status**: Local files ready for commit review (not staged, not committed, not pushed).





