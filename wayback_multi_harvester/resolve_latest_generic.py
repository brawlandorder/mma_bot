import sys, requests, os
from tqdm import tqdm

API = "https://archive.org/wayback/available"

def load_done(map_path):
    done = set()
    if os.path.exists(map_path):
        with open(map_path, "r", encoding="utf-8") as f:
            for line in f:
                if "\t" in line:
                    done.add(line.split("\t", 1)[0].strip())
    return done

def resolve(u):
    try:
        j = requests.get(API, params={"url": u}, timeout=30).json()
        c = j.get("archived_snapshots", {}).get("closest")
        if c and c.get("available"):
            return c["url"]
    except Exception:
        return None
    return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python resolve_latest_generic.py <input_urls.txt> <output_map.txt>")
        sys.exit(1)

    inp, out = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.dirname(out), exist_ok=True)

    already = load_done(out)
    appended = 0

    with open(inp, "r", encoding="utf-8") as fi, open(out, "a", encoding="utf-8") as fo:
        for line in tqdm(fi, desc=f"Resolving {os.path.basename(inp)}"):
            u = line.strip()
            if not u or u in already:
                continue
            s = resolve(u)
            if s:
                fo.write(f"{u}\t{s}\n")
                appended += 1

    print(f"Appended {appended} new mappings (skipped {len(already)} already done) -> {out}")

if __name__ == "__main__":
    main()