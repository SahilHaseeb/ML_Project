# PakSkillIQ — Persistent Antigravity Agent Guidelines & Master Log Rules

This document establishes permanent operational instructions and safety constraints for any AI coding assistant (Antigravity) working on the **PakSkillIQ** (Pakistan AI Job Market Intelligence Platform) codebase.

---

## 1. Mandatory Workflow: Master Log Maintenance

For **every future task** (regardless of whether it is a small bug fix, refactoring, feature addition, data task, testing, or deployment configuration):

### Pre-Task Execution:
1. **Read Master Log**: Always inspect `PROJECT_MASTER_LOG.md` at the project root before beginning any work to understand current status, recent decisions, and constraints.
2. **Follow Project Roadmap**: Ground all changes in the phase-by-phase roadmap established in `PROJECT_MASTER_LOG.md`.
3. **No Unprompted Changes**: Do not modify dashboard layouts, analytics logic, or collection pipelines unless explicitly instructed.

### Post-Task Execution:
Before ending the turn for any task, update `PROJECT_MASTER_LOG.md` with:
- **Date**: Current timestamp of update.
- **User Task / Prompt**: The user's request and its core objective.
- **What Was Completed**: Accurate, honest breakdown of what was actually achieved (never mark unfinished or unverified work as complete).
- **Files Affected**: Exact list of files created, modified, or deleted.
- **Commands Executed**: Every terminal command run and its purpose.
- **Test Results**: Actual execution results from test runs or explicit verification commands.
- **Artifact & Git Status**: Explicitly specify whether changes are local only, staged, committed, pushed, or deployed.
- **Decisions & Known Limitations**: Non-obvious trade-offs, constraints, or obstacles discovered.
- **Next Recommended Step**: Logical next engineering step for the user.
- **User Constraints**: Any newly introduced constraints or preferences from the user.

*Note*: Preserve all previous historical entries in `PROJECT_MASTER_LOG.md`. Keep the chronological history intact while keeping Section 6 (Current Status & Next Steps) accurate and up to date.

---

## 2. GitHub Synchronization Policy for Documentation

The user has explicitly authorized automatic GitHub synchronization for documentation files under these strict parameters:
1. **Scope of Auto-Commit/Push**:
   - Only `PROJECT_MASTER_LOG.md` and this rule file (`AGENTS.md`) are authorized for automatic pushing when logging progress.
   - **NEVER** automatically stage, commit, or push application code (`app.py`, `pages/`, `src/`), raw data (`data/raw/`), processed datasets (`data/processed/`), environment files (`.env`), or credentials unless the user explicitly requests code or dataset commits.
2. **Safety & Verification**:
   - Use descriptive commit messages (e.g., `docs: update master project progress log for <feature>`).
   - Verify that `git push` succeeded before reporting completion.
   - If a push fails (network, authentication, conflicts), keep the updated local file intact, report the error honestly, and **never force-push** (`--force`).
   - Do not trigger unwanted Render application redeployments intentionally just to publish documentation.

---

## 3. Core Project Constraints & Safety Rules

1. **No Hallucinated / Fabricated Data**:
   - Never invent salaries, company names, cities, or skills. Missing fields must remain `None` or `NaN`.
2. **Location Classification Integrity**:
   - Strictly classify jobs into:
     - `pakistan_based`: Physical job in Pakistan.
     - `pakistan_eligible`: Worldwide remote jobs that Pakistani developers can apply for.
     - `international_only`: Jobs restricted to US/EU or other regions.
   - Never label an international or unrestricted remote job as physical Pakistan without explicit evidence.
3. **Do Not Re-run Collection APIs Without Request**:
   - Do not call `src/collection/runner.py`, Remotive API, or Arbeitnow API during routine checks or documentation tasks.
4. **Preserve Sample Dataset**:
   - `data/sample/sample_jobs.csv` must remain intact and accessible as a separate option in the dashboard selector.
5. **Clear Explanation Style**:
   - Explain technical concepts and changes simply in plain English (or Roman English as requested by the user) so that a university student can understand, maintain, and present the project.
