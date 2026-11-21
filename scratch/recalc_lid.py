import json, sys
from collections import Counter, defaultdict

fixtures = []
with open('PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            fixtures.append(json.loads(line))

# CORRECTED mapping — all 5 categories are TANGLISH
CAT_MAP = {
    'TAMIL_SCRIPT_ENGLISH_TECH': 'TANGLISH',
    'ROMANIZED_TAMIL_INFORMAL': 'TANGLISH',
    'ENGLISH_TAMIL_COLLOQUIAL': 'TANGLISH',
    'INTRA_SENTENTIAL_CODE_SWITCH': 'TANGLISH',
    'FORMAL_TECHNICAL_TANGLISH': 'TANGLISH',
    'DISCOURSE_PARTICLE_MIX': 'TANGLISH',
}

sys.path.insert(0, 'scripts')
from language_identifier_v2 import LanguageIdentifierV2
lid = LanguageIdentifierV2()

y_true = []
y_pred = []
per_cat = defaultdict(lambda: {'total':0,'correct':0,'preds':Counter()})

for fix in fixtures:
    text = fix.get('text','')
    cat = fix.get('category','')
    expected = CAT_MAP.get(cat, 'UNKNOWN')
    r = lid.identify(text)
    pred = r.label
    y_true.append(expected)
    y_pred.append(pred)
    per_cat[cat]['total'] += 1
    per_cat[cat]['preds'][pred] += 1
    if pred == expected:
        per_cat[cat]['correct'] += 1

correct = sum(1 for a,b in zip(y_true,y_pred) if a==b)
acc = correct / len(y_true)
print(f"CORRECTED Overall accuracy: {acc:.2%} ({correct}/{len(y_true)})")
for cat in sorted(per_cat):
    d = per_cat[cat]
    a = d['correct']/d['total']
    preds_str = dict(d['preds'])
    print(f"  {cat}: {a:.2%} ({d['correct']}/{d['total']}) -> {preds_str}")

# Per-class P/R/F1
labels = sorted(set(y_true + y_pred))
for label in labels:
    tp = sum(1 for a,b in zip(y_true,y_pred) if a==label and b==label)
    fp = sum(1 for a,b in zip(y_true,y_pred) if a!=label and b==label)
    fn = sum(1 for a,b in zip(y_true,y_pred) if a==label and b!=label)
    p = tp/(tp+fp) if (tp+fp)>0 else 0
    r2 = tp/(tp+fn) if (tp+fn)>0 else 0
    f = 2*p*r2/(p+r2) if (p+r2)>0 else 0
    print(f"  {label}: P={p:.4f} R={r2:.4f} F1={f:.4f} (TP={tp} FP={fp} FN={fn})")

# Save corrected metrics to JSON
corrected = {
    "overall_accuracy": round(acc, 4),
    "total_correct": correct,
    "total_incorrect": len(y_true) - correct,
    "per_category": {},
}
for cat in sorted(per_cat):
    d = per_cat[cat]
    corrected["per_category"][cat] = {
        "total": d['total'],
        "correct": d['correct'],
        "accuracy": round(d['correct']/d['total'], 4),
        "predictions": dict(d['preds']),
    }

corrected["per_class"] = {}
for label in labels:
    tp = sum(1 for a,b in zip(y_true,y_pred) if a==label and b==label)
    fp = sum(1 for a,b in zip(y_true,y_pred) if a!=label and b==label)
    fn = sum(1 for a,b in zip(y_true,y_pred) if a==label and b!=label)
    p = tp/(tp+fp) if (tp+fp)>0 else 0
    r2 = tp/(tp+fn) if (tp+fn)>0 else 0
    f = 2*p*r2/(p+r2) if (p+r2)>0 else 0
    corrected["per_class"][label] = {"P": round(p,4), "R": round(r2,4), "F1": round(f,4)}

with open(r'C:\IGRIS\scratch\phase24_lid_corrected.json', 'w') as fout:
    json.dump(corrected, fout, indent=2)
print(f"\nCorrected metrics saved.")
