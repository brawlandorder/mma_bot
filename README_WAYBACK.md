# Wayback Machine Harvester (Drop-in)

This pack lets your repo **pull UFC sources from the Internet Archive (Wayback)** to avoid live-site blocking.

## What it does
- **`scripts/cdx_index.py`** — queries Wayback **CDX** for UFC-related URL patterns (UFCStats, Sherdog, Tapology, MMA Decisions, ESPN, Wikipedia) and writes `data/master_source_index.csv`.
- **`scripts/wayback_harvester.py`** — downloads archived snapshots listed in that CSV into `data/snapshots/{domain}/{timestamp}.html` with retry + rate-limit handling.
- **GitHub Action (`.github/workflows/wayback.yml`)** — one-click run from the **Actions** tab to build the index and download snapshots, even if live sites block scraping.

## Quickstart (local)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1) Build CDX index (patterns are baked in; adjust with --patterns)
python scripts/cdx_index.py --out data/master_source_index.csv --log-level INFO

# 2) Download snapshots (all domains)
python scripts/wayback_harvester.py --cdx-csv data/master_source_index.csv --max 500 --log-level INFO

# Or just Sherdog first
python scripts/wayback_harvester.py --cdx-csv data/master_source_index.csv --domain-filter sherdog.com --max 1000
```

## GitHub Actions (no local setup required)
- Go to **Actions → Wayback Harvester → Run workflow**.
- Choose:
  - `run_cdx`: `true` (build a fresh index) or `false` (reuse committed CSV)
  - `domain_filter`: e.g., `sherdog.com` to start
  - `max_downloads`: e.g., `2000`

Artifacts (snapshots) appear under the workflow run. You can also push them to the repo if desired.

## Notes
- We **collapse by digest** in CDX to reduce duplicates.
- Defaults fetch status **200** only; loosen with `--filter-status ""` if needed.
- Add/remove patterns inside `scripts/cdx_index.py` (`DEFAULT_PATTERNS`).
- This is designed to **feed your UFC CSV builder/validator** so it can operate from archived HTML instead of the live web, matching your reproducibility requirements.
