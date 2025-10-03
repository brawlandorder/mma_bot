#!/usr/bin/env python3

import argparse
import csv
import sys
import time
import logging
import requests
from typing import List, Dict
from urllib.parse import quote
from common import jitter_sleep, build_ua, setup_logging

CDX_URL = "https://web.archive.org/cdx/search/cdx"

# Helpful patterns for our sources. You can add/remove patterns here.
DEFAULT_PATTERNS = [
    # UFCStats (FightMetric)
    "ufcstats.com/event-details*",
    "ufcstats.com/fight-details*",
    "ufcstats.com/statistics/events/*",
    # Sherdog
    "sherdog.com/events/UFC-*",
    "sherdog.com/fight/*",
    "sherdog.com/news/*",
    # Tapology
    "tapology.com/fightcenter/events/*-ufc-*",
    "tapology.com/fightcenter/bouts/*-ufc-*",
    # MMA Decisions
    "mmadecisions.com/event/*",
    # ESPN (as fallback metadata; broad to narrow as needed)
    "espn.com/mma/fight/_/id/*",
    "espn.com/mma/event/_/id/*",
    # Wikipedia (last-resort metadata; still capture snapshots for reproducibility)
    "en.wikipedia.org/wiki/UFC_*",
]

def fetch_cdx(pattern: str, from_year: str, to_year: str, limit: int, filter_status: str) -> List[Dict[str, str]]:
    """
    Query CDX API for a given pattern.
    Returns list of dicts with keys: timestamp, original, statuscode, digest, length, mime
    """
    params = {
        "url": pattern,
        "from": from_year,
        "to": to_year,
        "output": "json",
        "fl": "timestamp,original,statuscode,digest,length,mime",
        "filter": f"statuscode:{filter_status}" if filter_status else None,
        "collapse": "digest",   # de-duplicate identical content
        "limit": str(limit) if limit else None,
    }
    # Remove None entries
    params = {k: v for k, v in params.items() if v is not None}

    headers = {"User-Agent": build_ua()}
    tries = 0
    out = []
    while tries < 5:
        tries += 1
        try:
            r = requests.get(CDX_URL, params=params, headers=headers, timeout=30)
            if r.status_code == 429:
                logging.warning("CDX 429 rate-limited. Backing off...")
                time.sleep(2 * tries)
                continue
            r.raise_for_status()
            data = r.json()
            if not data:
                return []
            # First row is header
            header = data[0]
            for row in data[1:]:
                rec = dict(zip(header, row))
                out.append(rec)
            return out
        except Exception as e:
            logging.warning(f"CDX fetch error for pattern {pattern!r}: {e}. Retry {tries}/5")
            time.sleep(1.5 * tries)
    return out

def main():
    ap = argparse.ArgumentParser(description="Query Wayback CDX for URL patterns and write an index CSV.")
    ap.add_argument("--patterns", nargs="*", default=None, help="URL glob patterns for CDX (e.g., 'sherdog.com/events/UFC-*')")
    ap.add_argument("--from-year", default="1993", help="Start year (YYYY)")
    ap.add_argument("--to-year", default="2025", help="End year (YYYY)")
    ap.add_argument("--limit", type=int, default=0, help="Max results per pattern (0 = no limit)")
    ap.add_argument("--filter-status", default="200", help="Filter status code (e.g., 200). Blank to disable.")
    ap.add_argument("--out", default="data/master_source_index.csv", help="Output CSV path")
    ap.add_argument("--log-level", default="INFO", help="Logging level")
    args = ap.parse_args()

    setup_logging(args.log_level)

    patterns = args.patterns or DEFAULT_PATTERNS
    logging.info(f"Starting CDX index across {len(patterns)} patterns → {args.out}")

    rows = []
    for pat in patterns:
        logging.info(f"Fetching CDX for pattern: {pat}")
        recs = fetch_cdx(pat, args.from_year, args.to_year, args.limit, args.filter_status)
        logging.info(f"  → {len(recs)} records")
        rows.extend(recs)
        jitter_sleep()

    # Ensure output folder exists
    import os
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    # Write CSV
    fieldnames = ["timestamp", "original", "statuscode", "digest", "length", "mime"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})

    logging.info(f"Wrote {len(rows)} CDX rows to {args.out}")
    logging.info("Done.")

if __name__ == "__main__":
    sys.exit(main())
