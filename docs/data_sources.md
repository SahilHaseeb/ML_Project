# Data Sources — Pakistan AI Job Market Intelligence Platform

## Active Data Sources (Phase 2)

### 1. Remotive Public API (`remotive_api`)

| Property | Value |
|----------|-------|
| API Endpoint | `https://remotive.com/api/remote-jobs` |
| Access Type | Public developer REST API |
| Terms of Service | Permitted for non-commercial, personal, and educational research projects. Attribution and direct job URL linking required. |
| Fields Captured | `id`, `url`, `title`, `company_name`, `candidate_required_location`, `category`, `job_type`, `publication_date`, `salary`, `description`, `tags` |
| Raw Archive | `data/raw/remotive_api_raw_<timestamp>.json` |
| **Pakistan Limitations** | Remotive is an international remote tech job board. It provides almost **no domestic on-site Pakistan listings**. Positions accessible to Pakistani talent are strictly identified when `candidate_required_location` is explicitly **"Worldwide"**, **"Anywhere"**, or contains **"Pakistan"**. All other roles restricted to specific regions (e.g., "USA Only", "Europe Only") are strictly classified as `Restricted Remote (Non-Pakistan)`. |

---

### 2. Arbeitnow Public Job Board API (`arbeitnow_api`)

| Property | Value |
|----------|-------|
| API Endpoint | `https://www.arbeitnow.com/api/job-board-api` |
| Access Type | Open job board API for developers |
| Terms of Service | Free public API for job aggregators and developer integration with source link attribution. |
| Fields Captured | `slug`, `title`, `company_name`, `location`, `remote`, `tags`, `job_types`, `created_at`, `url`, `description` |
| Raw Archive | `data/raw/arbeitnow_api_raw_<timestamp>.json` |
| **Pakistan Limitations** | Arbeitnow is primarily focused on European and remote tech employers. It does **not** feature local Pakistani corporate employers. Roles with `remote: True` and no geographical limitation are marked as `Pakistan-Eligible (Worldwide Remote)`, while localized physical offices are marked as `International (On-site)`. |

---

### 3. Local Feeds & Open Records (`local_feed`)

| Property | Value |
|----------|-------|
| Ingestion Mechanism | `src.collection.api_collectors.LocalRawFileCollector` |
| Formats Supported | Raw CSV / JSON placed in `data/raw/` |
| Purpose | Enables ingesting verified local Pakistan job dumps (e.g. PSEB open lists, community technology job archives) without modifying raw payloads. |

---

### 4. Phase 1 Synthetic Sample Dataset (`sample`)

| Property | Value |
|----------|-------|
| File | `data/sample/sample_jobs.csv` |
| Rows | 50 synthetic job listings |
| Purpose | Backward-compatibility, testing, and UI demonstration when offline. |

---

## Geographic Scope Classification Rules

To prevent misleading students and researchers, the platform enforces strict classification rules. **A job is NEVER labeled as Pakistan-based without direct factual evidence**:

1. **`Pakistan (On-site / Hybrid)`**: Only assigned when the location explicitly contains a recognized Pakistani city (`Karachi`, `Lahore`, `Islamabad`, `Rawalpindi`, `Peshawar`, `Faisalabad`, `Multan`, `Quetta`, `Sialkot`, etc.) or the country name `"Pakistan"`.
2. **`Pakistan (Remote / Hybrid)`**: Assigned when an employer in Pakistan offers remote or hybrid work.
3. **`Pakistan-Eligible (Worldwide Remote)`**: Assigned when candidate eligibility is explicitly declared as `"Worldwide"`, `"Anywhere"`, or `"Work from anywhere"`.
4. **`Restricted Remote (Non-Pakistan)`**: Assigned when a remote job restricts candidate location to non-Pakistan regions (`USA Only`, `Europe Only`, `UK Only`, `Canada Only`, etc.).
5. **`International (On-site)`**: Non-remote physical job locations outside Pakistan (e.g., `Berlin, Germany`).

---

## Ethical Guidelines

1. **Permission First**: Only use permitted public developer APIs or sources whose terms explicitly permit automated access.
2. **Never Bypass Restrictions**: Do not circumvent Cloudflare, CAPTCHAs, bot detections, or paywalls.
3. **Strict Separation**: Original raw payloads are archived untouched in `data/raw/` before any cleaning begins.
4. **No Invention**: Never fabricate missing salaries, experience levels, company names, or skills. Missing values are left as `NaN` / `None`.
5. **Rate Limiting**: Enforce respectful delays (minimum 2.0s) between HTTP requests.
6. **No Personal Data**: Do not scrape or store personal data, applicant CVs, or contact information.
