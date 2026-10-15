# Data Schema — Pakistan AI Job Market Intelligence Platform

## Overview

Each job listing is stored as one row in the CSV and (eventually) the PostgreSQL database.
Fields are chosen to be the minimum useful set — we never invent values for missing fields.

## Field Definitions

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `job_id` | string | ✅ Yes | Unique identifier (UUID or source ID) |
| `title` | string | ✅ Yes | Original job title from the source |
| `company` | string | Optional | Company name; may be "Confidential" or missing |
| `location` | string | Optional | Raw location; normalized to canonical city name |
| `category` | string | Optional | Technology category; normalized |
| `salary_min` | float | Optional | Minimum salary; **never estimated if not disclosed** |
| `salary_max` | float | Optional | Maximum salary |
| `salary_currency` | string | Optional | "PKR" / "USD" / unknown |
| `experience_min` | float | Optional | Minimum years of experience required |
| `experience_max` | float | Optional | Maximum years (or ceiling) of experience |
| `education` | string | Optional | "BS", "MS", "PhD", "Diploma", etc. |
| `job_type` | string | Optional | "Full-time", "Part-time", "Remote", "Contract" |
| `skills` | string | Optional | Pipe-separated: `"Python\|Django\|SQL"` |
| `description` | string | Optional | Full job description text |
| `posting_date` | date | Optional | YYYY-MM-DD; stored as datetime after parsing |
| `source` | string | ✅ Yes | Data source name: "sample", "rozee.pk", etc. |
| `job_url` | string | Optional | Direct URL to the original listing |
| `scraped_at` | datetime | ✅ Yes | ISO 8601 timestamp of when we collected this row |

## Conventions

- Missing values are stored as `NULL` (in DB) or `NaN` (in DataFrame) — never as zero, empty string, or invented value.
- The `skills` pipe-separator is `|` (pipe character).
- `salary_min` / `salary_max` are the disclosed range, not estimates.
- If only one salary value is given, it goes into `salary_min` and `salary_max` is `NULL`.
- `posting_date` is the date the employer posted the job, **not** when we scraped it.

## PostgreSQL Schema (Phase 5)

```sql
-- Core jobs table
CREATE TABLE jobs (
    job_id          VARCHAR(64) PRIMARY KEY,
    title           TEXT NOT NULL,
    company         TEXT,
    location        TEXT,
    category        TEXT,
    salary_min      NUMERIC(12,2),
    salary_max      NUMERIC(12,2),
    salary_currency VARCHAR(10),
    experience_min  NUMERIC(4,1),
    experience_max  NUMERIC(4,1),
    education       TEXT,
    job_type        TEXT,
    description     TEXT,
    posting_date    DATE,
    source          TEXT NOT NULL,
    job_url         TEXT,
    scraped_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Normalized skills table
CREATE TABLE skills (
    skill_id    SERIAL PRIMARY KEY,
    skill_name  TEXT UNIQUE NOT NULL
);

-- Many-to-many relationship: one job ↔ many skills
CREATE TABLE job_skills (
    job_id      VARCHAR(64) REFERENCES jobs(job_id) ON DELETE CASCADE,
    skill_id    INTEGER REFERENCES skills(skill_id) ON DELETE CASCADE,
    PRIMARY KEY (job_id, skill_id)
);

-- Index for fast skill lookups
CREATE INDEX idx_job_skills_skill_id ON job_skills(skill_id);
CREATE INDEX idx_jobs_category ON jobs(category);
CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_jobs_posting_date ON jobs(posting_date);
```
