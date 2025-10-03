#!/usr/bin/env python3

import argparse
import csv
import os
import sys
import time
import logging
import requests
from typing import Optional
from urllib.parse import quote
from common import jitter_sleep, build_ua, setup_logging

WAYBACK_FETCH = "https://web.archive.org/web/{timestamp}id_/{original}"

def fetch_snapshot(timestamp: str, original: str, out_path: str, overwrite: bool = False) -> bool:
    if (not overwrite) and os.path.exists(out_path):
        logging.debug(f"Skip existing: {out_path}")
        return True

    headers = {"User-Agent": build_ua()}
    url = WAYBACK_FETCH.format(timestamp=timestamp, original=original)
    tries = 0
    while tries < 5:
        tries += 1
        try:
            r = requests.get(url, headers=headers, timeout=60)
            if r.status_code == 429:
                logging.warning("Wayback 429 rate-limited. Backing off...")
                time.sleep(2 * tries)
                continue
            if r.status_code == 404:
                logging.warning(f"Snapshot missing 404 for {timestamp} {original}")
                return False
            r.raise_for_status()
            with open(out_path, "wb") as f:
                f.write(r.content)
            return True
        except Exception as e:
            logging.warning(f"Fetch error for {timestamp} {original}: {e}. Retry {tries}/5")
            time.sleep(1.5 * tries)
    return False

def main():
    ap = argparse.ArgumentParser(description="Download archived snapshots listed in a CDX CSV.")
    ap.add_argument("--cdx-csv", default="data/master_source_index.csv", help="CDX index CSV path")
    ap.add_argument("--domain-filter", default="", help="Only download rows where original contains this string (e.g., 'sherdog.com')")
    ap.add_argument("--max", type=int, default=0, help="Max snapshots to download (0 = no limit)")
    ap.add_argument("--out-dir", default="data/snapshots", help="Directory to save snapshots")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    ap.add_argument("--log-level", default="INFO", help="Logging level")
    args = ap.parse_args()

    setup_logging(args.log_level)

    if not os.path.exists(args.cdx_csv):
        logging.error(f"CDX CSV not found: {args.cdx_csv}. Run cdx_index.py first.")
        return 1

    os.makedirs(args.out_dir, exist_ok=True)

    count = 0
    with open(args.cdx_csv, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            ts = row.get("timestamp", "").strip()
            orig = row.get("original", "").strip()
            if not ts or not orig:
                continue
            if args.domain_filter and (args.domain_filter not in orig):
                continue

            # Make a clean nested path: data/snapshots/{domain}/{timestamp}.html
            # More granular paths can be added later.
            domain = orig.split("/")[2] if "://" in orig else "unknown"
            domain_dir = os.path.join(args.out_dir, domain)
            os.makedirs(domain_dir, exist_ok=True)

            out_path = os.path.join(domain_dir, f"{ts}.html")
            ok = fetch_snapshot(ts, orig, out_path, overwrite=args.overwrite)
            if ok:
                count += 1
                logging.info(f"[{count}] Saved {domain}/{ts}.html")
            jitter_sleep()

            if args.max and count >= args.max:
                break

    logging.info(f"Downloaded {count} snapshot(s) to {args.out_dir}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
