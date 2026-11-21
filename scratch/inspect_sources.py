import csv
from pathlib import Path

p = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
for fname in ["IGRIS_PHASE13_SOURCE_AUTHORIZATION_REGISTER.csv", "DATASET_SOURCE_CATALOG_V3.csv", "PHASE21_SOURCE_LICENSE_REVIEW.csv", "IGRIS_PHASE10_SOURCE_ELIGIBILITY_RECONCILIATION.csv"]:
    fpath = p / fname
    if fpath.exists():
        with open(fpath, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            print(f"=== {fname} ({len(reader)} rows) ===")
            if reader:
                print("Fieldnames:", list(reader[0].keys()))
                print("Sample row 0:", reader[0])
