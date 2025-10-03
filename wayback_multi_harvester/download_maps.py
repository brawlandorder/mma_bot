import os, sys, requests
from tqdm import tqdm

USAGE = "Usage: python download_maps.py <mapping_file> <out_dir>"

def main():
    if len(sys.argv) < 3:
        print(USAGE); sys.exit(1)

    mapping, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    sess = requests.Session()
    sess.headers.update({"User-Agent": "Mozilla/5.0"})

    saved = 0
    skipped = 0
    total = 0

    with open(mapping, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc=f"Downloading {os.path.basename(mapping)}"):
            parts = line.strip().split("\t")
            if len(parts) != 2:
                continue
            orig, snap = parts
            total += 1

            tail = orig.strip("/").split("/")[-1] or "page"
            out_path = os.path.join(out_dir, f"{tail}_wayback.html")

            if os.path.exists(out_path):
                skipped += 1
                continue

            try:
                r = sess.get(snap, timeout=60)
                if r.status_code == 200:
                    with open(out_path, "w", encoding="utf-8") as fh:
                        fh.write(r.text)
                    saved += 1
            except Exception:
                pass

    print(f"\nDone -> {out_dir}")
    print(f"  Total mappings: {total}")
    print(f"  Saved:          {saved}")
    print(f"  Skipped:        {skipped} (already existed)")

if __name__ == "__main__":
    main()