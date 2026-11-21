import json

with open(r'C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\PHASE25_SYNTHETIC_DATASET_MANIFEST.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

records = data['records']
print('Total records in manifest:', len(records))

# Find records where ground truth was ENGLISH but predicted was TANGLISH
misclassified_en = []
for r in records:
    gt_lang = r['metadata'].get('ground_truth_language')
    pred_lang = r['language_label']
    if gt_lang == 'ENGLISH' and pred_lang == 'TANGLISH':
        misclassified_en.append(r)

print(f'\nGround truth ENGLISH predicted TANGLISH: {len(misclassified_en)}')
for r in misclassified_en:
    print(f"ID={r['id']} Sublabel={r['language_sublabel']} Cat={r['metadata'].get('category')}")
    print(f"  Text: {r['original_text']}")

# Find the 2 incorrect quality filter decisions
qf_mismatches = []
for r in records:
    exp_q = r['metadata'].get('expected_quality_pass')
    act_q = r['quality_passed']
    if exp_q != act_q:
        qf_mismatches.append(r)

print(f'\nQuality filter mismatches: {len(qf_mismatches)}')
for r in qf_mismatches:
    print(f"ID={r['id']} Exp={r['metadata'].get('expected_quality_pass')} Act={r['quality_passed']} Reasons={r['quality_reasons']}")
    print(f"  Text: {r['original_text']}")
