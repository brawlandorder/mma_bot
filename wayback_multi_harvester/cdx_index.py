import json, requests, os
from tqdm import tqdm

def cdx_fetch(pattern, cdx, base_params):
    """Fetch a URL list from Wayback CDX. Returns originals; safe on empty/odd responses."""
    try:
        params = dict(base_params)
        params["url"] = pattern
        r = requests.get(cdx, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()
        if not data:
            return []
        header = data[0]
        # If the first row isn't a header, treat all rows as data lists
        if isinstance(header, list) and "original" not in header:
            rows = data
            originals = [row[2].strip() for row in rows if isinstance(row, list) and len(row) >= 3]
        else:
            rows = data[1:]
            originals = [dict(zip(header, row))["original"].strip() for row in rows]
        # dedup preserve order
        seen, out = set(), []
        for u in originals:
            if u and u not in seen:
                out.append(u); seen.add(u)
        return out
    except Exception:
        return []

def write_list(path, urls):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(urls))

def main():
    cfg = json.load(open("config.json", "r"))
    CDX = cfg["cdx_endpoint"]
    BASE = cfg["cdx_params"]

    os.makedirs("indexes", exist_ok=True)

    # Tapology: try several patterns and merge (often returns 0; that's OK)
    tapology_variants = [
        "www.tapology.com/fightcenter/events/*-ufc-*",
        "www.tapology.com/fightcenter/events/*ufc*",
        "tapology.com/fightcenter/events/*-ufc-*",
        "tapology.com/fightcenter/events/*ufc*"
    ]

    for src in cfg["sources"]:
        name, pattern = src["name"], src["pattern"]
        out_file = os.path.join("indexes", f"{name}.txt")
        print(f"[index] {name}: {pattern}")

        # Special handling: Tapology merged variants
        if name == "tapology_events":
            merged = []
            for pat in tapology_variants:
                urls = cdx_fetch(pat, CDX, BASE)
                print(f"  -> {len(urls)} via {pat}")
                merged.extend(urls)
            # dedup
            seen, deduped = set(), []
            for u in merged:
                if u not in seen:
                    deduped.append(u); seen.add(u)
            write_list(out_file, deduped)
            print(f"  == total Tapology deduped: {len(deduped)} -> {out_file}")
            continue

        # Normal case (Sherdog, Wikipedia, MMAJunkie, MMADecisions, UFCStats, ESPN variants)
        urls = cdx_fetch(pattern, CDX, BASE)
        print(f"  -> {len(urls)} URLs")
        write_list(out_file, urls)

if __name__ == "__main__":
    main()