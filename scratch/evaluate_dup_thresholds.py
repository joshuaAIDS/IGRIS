import json, sys
sys.path.insert(0, r'C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\scripts')
from duplicate_detector_v2 import DuplicateDetectorV2

with open(r'C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\PHASE26_DATASET_SPLITS.json', 'r', encoding='utf-8') as f:
    pkg = json.load(f)

val_records = pkg['splits']['val']

thresholds = [0.70, 0.75, 0.80, 0.85, 0.90]
results = {}

for th in thresholds:
    dd = DuplicateDetectorV2(near_dup_threshold=th)
    tp = tn = fp = fn = 0
    for r in val_records:
        text = r['text']
        if not text.strip():
            continue
        exp_dup = r['expected_duplicate']
        res = dd.check_and_register(r['id'], text)
        is_dup = res.is_duplicate
        if exp_dup and is_dup:
            tp += 1
        elif not exp_dup and not is_dup:
            tn += 1
        elif not exp_dup and is_dup:
            fp += 1
        else:
            fn += 1
    p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r_val = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * p * r_val / (p + r_val) if (p + r_val) > 0 else 0.0
    results[th] = {"precision": round(p, 4), "recall": round(r_val, 4), "f1": round(f1, 4), "tp": tp, "tn": tn, "fp": fp, "fn": fn}
    print(f"Threshold {th:.2f}: P={p:.4f}, R={r_val:.4f}, F1={f1:.4f} (TP={tp}, TN={tn}, FP={fp}, FN={fn})")
