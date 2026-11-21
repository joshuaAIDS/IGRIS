import json

with open(r'C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\PHASE26_DATASET_SPLITS.json', 'r', encoding='utf-8') as f:
    pkg = json.load(f)

splits = pkg['splits']
dev_texts = set(r['text'] for r in splits['dev'])
val_texts = set(r['text'] for r in splits['val'])
test_texts = set(r['text'] for r in splits['test'])

print(f"Dev count: {len(splits['dev'])} (unique texts: {len(dev_texts)})")
print(f"Val count: {len(splits['val'])} (unique texts: {len(val_texts)})")
print(f"Test count: {len(splits['test'])} (unique texts: {len(test_texts)})")

dev_val_overlap = dev_texts & val_texts
dev_test_overlap = dev_texts & test_texts
val_test_overlap = val_texts & test_texts

print(f"Dev <-> Val overlap: {len(dev_val_overlap)}")
print(f"Dev <-> Test overlap: {len(dev_test_overlap)}")
print(f"Val <-> Test overlap: {len(val_test_overlap)}")

# Verify schema
required_fields = [
    "id", "text", "ground_truth_language", "category",
    "expected_processing_behavior", "difficulty", "provenance",
    "dataset_split", "expected_quality_pass", "expected_duplicate",
    "expected_rejection_reasons", "notes"
]
for split_name, recs in splits.items():
    for r in recs:
        for rf in required_fields:
            if rf not in r:
                print(f"Missing field {rf} in {r.get('id')}")

print("Schema verification complete.")
