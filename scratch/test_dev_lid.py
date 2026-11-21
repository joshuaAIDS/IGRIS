import json, sys
from collections import Counter
sys.path.insert(0, r'C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\scripts')
from language_identifier_v2 import LanguageIdentifierV2

with open(r'C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\PHASE26_DATASET_SPLITS.json', 'r', encoding='utf-8') as f:
    pkg = json.load(f)

dev_records = pkg['splits']['dev']
lid = LanguageIdentifierV2()

correct = 0
total = len(dev_records)
mismatches = []

for r in dev_records:
    res = lid.identify(r['text'])
    gt = r['ground_truth_language']
    if res.label == gt:
        correct += 1
    else:
        mismatches.append({
            'id': r['id'],
            'gt': gt,
            'pred': res.label,
            'sub': res.sublabel,
            'diff': r['difficulty'],
            'cat': r['category'],
            'text': r['text'][:60]
        })

print(f"Dev accuracy: {correct}/{total} ({correct/total:.2%})")
print(f"Total mismatches: {len(mismatches)}")
for m in mismatches:
    print(f"  {m['id']} [{m['gt']} -> {m['pred']}] ({m['diff']}) {m['cat']}: {m['text']}")
