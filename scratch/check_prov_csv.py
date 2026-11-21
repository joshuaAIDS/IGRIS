import csv
from collections import Counter
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
prov_file = PATCH_ROOT / "CANDIDATE_A_PROVENANCE_AUDIT.csv"

with open(prov_file, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print(f"Total rows in CANDIDATE_A_PROVENANCE_AUDIT.csv: {len(rows)}")
counts = Counter(r["language_classification"] for r in rows)
print(f"Counts: {counts}")
