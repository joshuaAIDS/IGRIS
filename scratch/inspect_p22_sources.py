import csv
with open(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\PHASE22_SOURCE_OWNER_DECISION_REGISTER.csv", "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

for r in rows:
    print(f"{r['source_id']} | {r['dataset_name']} | {r['language_coverage']} | {r['published_license']} | {r['initial_eligibility_class']} | {r['legal_review_status']}")
