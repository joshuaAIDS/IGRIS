import csv
from pathlib import Path

p = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")

sources_v3 = {}
with open(p / "DATASET_SOURCE_CATALOG_V3.csv", "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        sources_v3[row["source_id"]] = row

sources_auth = {}
with open(p / "IGRIS_PHASE13_SOURCE_AUTHORIZATION_REGISTER.csv", "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        sources_auth[row["source_id"]] = row

sources_p21 = set()
with open(p / "PHASE21_SOURCE_LICENSE_REVIEW.csv", "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        sources_p21.add(row["source_id"])

print(f"Total sources in Catalog V3: {len(sources_v3)}")
print(f"Total sources in Auth Register: {len(sources_auth)}")
print(f"Total sources in Phase 21 Eligible: {len(sources_p21)}")

# Let's inspect test_phase21_controlled_dataset_preparation.py or test_phase20* to see how tests classify the 32 sources
for test_f in ["test_phase20_final_readiness.py", "test_phase21_controlled_dataset_preparation.py", "test_phase21a_tokenizer_selection_and_dataset_review.py"]:
    tpath = p / "tests" / test_f
    if tpath.exists():
        with open(tpath, "r", encoding="utf-8") as f:
            content = f.read()
            for kw in ["18", "conditional", "incompatible", "evaluation-only", "32"]:
                if kw in content.lower():
                    print(f"Found '{kw}' in {test_f}")
