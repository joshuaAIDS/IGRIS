import csv
from collections import Counter
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
split_manifest = PATCH_ROOT / "CANDIDATE_A_SYNTHETIC_SPLIT_MANIFEST.csv"
prov_audit = PATCH_ROOT / "CANDIDATE_A_PROVENANCE_AUDIT.csv"

with open(split_manifest, encoding="utf-8") as f:
    s_rows = list(csv.DictReader(f))

with open(prov_audit, encoding="utf-8") as f:
    p_rows = list(csv.DictReader(f))

print(f"Split rows: {len(s_rows)}")
print(f"Prov rows: {len(p_rows)}")

# Check if there are any ID discrepancies
s_ids = [r["doc_id"] for r in s_rows]
p_ids = [r["doc_id"] for r in p_rows]
assert s_ids == p_ids

# Compare language column
matches = 0
diffs = []
for s, p in zip(s_rows, p_rows):
    sl = s["language"]
    pl = p["language_classification"]
    if sl == pl:
        matches += 1
    else:
        diffs.append((s["doc_id"], sl, pl))

print(f"Matches: {matches}, Differences: {len(diffs)}")

# Let's inspect the sources of the 399 records
src_counts = Counter(r["source_file"] for r in s_rows)
print("\nSources breakdown for 399 approved records:")
for src, cnt in src_counts.items():
    print(f"  {src}: {cnt}")

# Source x Language in split manifest:
src_lang = Counter((r["source_file"], r["language"]) for r in s_rows)
print("\nSource x Language in split manifest:")
for k, cnt in sorted(src_lang.items()):
    print(f"  {k[0]} -> {k[1]}: {cnt}")
