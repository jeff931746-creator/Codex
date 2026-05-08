# level_progress_analysis

Scratch workspace for level progress and churn analysis. This folder keeps the analysis reproducible while separating scripts, derived data, reports, and render checks.

## Layout

- `scripts/` — analysis, report generation, and verification scripts.
- `data/period_comparison/` — derived CSV/JSON data for the 1.09-1.11, 1.13-1.15, and 4.4-4.8 period comparison.
- `data/april_focus/` — derived CSV/JSON data for the April-focused churn analysis.
- `reports/` — generated `.xlsx` and `.docx` deliverables.
- `renders/full_doc/` — rendered image checks for the full document version.
- `renders/plain_doc/` — rendered image checks for the plain document version.
- `memory/` — task-state notes and memory-index snippets created during the analysis.

## Reuse Rules

- Treat `data/` as derived output. Regenerate it from `scripts/` when source workbooks change.
- Keep final deliverables in `reports/`; move durable reports to the relevant `projects/` or `research/` folder if they become part of ongoing work.
- Do not keep caches here. Remove `.DS_Store`, `__pycache__`, `node_modules`, downloaded runtimes, and package caches after use.
- If a script is reused for future analyses, promote it out of `tmp/` into `tools/` and update paths accordingly.

## Current Scripts

- `scripts/analyze_progress.py` writes period comparison outputs to `data/period_comparison/`.
- `scripts/build_report.mjs` reads `data/period_comparison/` and writes the 1.13-1.15 report to `reports/`.
- `scripts/analyze_april_churn.py` writes April-focused outputs to `data/april_focus/`.
- `scripts/build_april_focus_report.mjs` reads `data/april_focus/` and writes the April-focused workbook to `reports/`.
- `scripts/build_churn_analysis_doc.py` and `scripts/build_churn_analysis_doc_plain.py` read `data/april_focus/` and write document reports to `reports/`.
- `scripts/verify_report.mjs` and `scripts/verify_april_focus_report.mjs` verify generated workbooks in `reports/`.
