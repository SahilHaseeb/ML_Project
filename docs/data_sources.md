# Data Sources — Pakistan AI Job Market Intelligence Platform

## Current Data Sources

### Phase 1 — Synthetic Sample Dataset

| Property | Value |
|----------|-------|
| File | `data/sample/sample_jobs.csv` |
| Rows | 50 synthetic job listings |
| Real-world coverage | None |
| Created | 2024-10-01 |
| Purpose | Dashboard development & demonstration |

**⚠️ This data is entirely made up. Do not cite it as a real market statistic.**

---

## Planned Sources (Phase 4)

### Rozee.pk

- **Type:** Pakistan's largest job portal
- **Robots.txt:** Must check `https://www.rozee.pk/robots.txt` before scraping
- **ToS:** Must read and comply with Terms of Service
- **Rate limit:** Minimum 2–5 seconds between requests
- **Status:** ❌ Not yet confirmed — scraper is a stub only
- **Notes:** May offer an official API or data partnership for researchers

### Mustakbil.com

- **Type:** Pakistani job board
- **Robots.txt:** Must check before use
- **Status:** ❌ Not yet confirmed

### LinkedIn Jobs

- **Type:** Global job network with Pakistan listings
- **API:** LinkedIn Jobs Search API requires approval
- **Rate limit:** Strict — requires registered app
- **Status:** ❌ Requires API key and agreement

### PSEB / Government Sources

- **Type:** Pakistan Software Export Board open data
- **ToS:** Typically open data
- **Status:** 🔍 To be investigated

---

## Ethical Guidelines

1. **Always check robots.txt** before scraping any source.
2. **Read Terms of Service** — if scraping is prohibited, use official APIs or data partnerships.
3. **Respect rate limits** — the `BaseScraper` class enforces a configurable delay.
4. **Do not bypass authentication** — never log in to extract data not accessible to anonymous users.
5. **Do not store personal data** — job seekers' profiles, contact details, or CVs are not collected.
6. **Declare the source** — every collected row must have the `source` field set.
7. **Disclose limitations** — always state the coverage dates, source, and known gaps in the dashboard.
