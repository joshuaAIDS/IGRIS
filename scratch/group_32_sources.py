import csv
import json
from pathlib import Path

p = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\DATASET_SOURCE_CATALOG_V3.csv")
with open(p, "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

grouped = {
    "ELIGIBLE": [],
    "INELIGIBLE_CONDITIONAL": [],
    "INELIGIBLE_PROHIBITED": [],
    "INELIGIBLE_REJECTED": []
}

for r in rows:
    grouped[r["tokenizer_training_eligibility"]].append({
        "source_id": r["source_id"],
        "dataset_name": r["dataset_name"],
        "category": r["category"],
        "primary_language": r["primary_language"],
        "published_license": r["published_license"],
        "eligibility": r["tokenizer_training_eligibility"],
        "provenance_type": r["provenance_type"],
        "size": r["published_size_estimate"]
    })

print("Categories count:")
for k, v in grouped.items():
    print(f"  {k}: {len(v)}")
    for item in v:
        print(f"    - {item['source_id']}: {item['dataset_name']} ({item['published_license']}, {item['primary_language']})")

with open(r"C:\IGRIS\scratch\all_32_sources.json", "w", encoding="utf-8") as f:
    json.dump(grouped, f, indent=2)
