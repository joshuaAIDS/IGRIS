"""
Phase 27 Entry Task: Independent recalculation of Phase 26 HELD-OUT TEST SET metrics
from the saved per-record predictions in PHASE26_TEST_RESULTS.json.
"""
import json
import sys
from collections import defaultdict

RESULTS_PATH = r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\PHASE26_TEST_RESULTS.json"

with open(RESULTS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 72)
print("PHASE 26 HELD-OUT TEST SET — INDEPENDENT METRIC RECALCULATION")
print("=" * 72)

discrepancies = []

# ── All three splits to check ──
splits_config = [
    ("DEV", data["development_set_metrics"], data["development_set_metrics"]),
    ("VAL", data["validation_set_metrics"], data["validation_set_metrics"]),
    ("TEST (held-out)", data["held_out_test_set_metrics"]["language_identification"],
     data["held_out_test_set_metrics"]["language_identification"]),
]

for split_label, reported, detail_source in splits_config:
    details = detail_source.get("details", [])
    if not details:
        print(f"\n--- {split_label}: NO DETAIL RECORDS FOUND ---")
        continue

    print(f"\n{'='*72}")
    print(f"  SPLIT: {split_label} ({len(details)} records)")
    print(f"{'='*72}")

    # Recalculate accuracy
    correct = sum(1 for d in details if d["correct"])
    total = len(details)
    recalc_accuracy = correct / total if total > 0 else 0.0

    print(f"  Reported accuracy:      {reported['accuracy']}")
    print(f"  Recalculated accuracy:  {recalc_accuracy} ({correct}/{total})")
    if abs(recalc_accuracy - reported['accuracy']) > 1e-6:
        discrepancies.append(f"{split_label}: accuracy reported={reported['accuracy']} recalc={recalc_accuracy}")

    # Verify correct flag matches true==pred
    flag_errors = []
    for d in details:
        expected_correct = (d["true"] == d["pred"])
        if d["correct"] != expected_correct:
            flag_errors.append(d)
    if flag_errors:
        print(f"\n  [DISCREPANCY] {len(flag_errors)} records have incorrect 'correct' flag:")
        for d in flag_errors:
            print(f"    {d['id']}: true={d['true']} pred={d['pred']} flag={d['correct']} expected={d['true']==d['pred']}")
        discrepancies.append(f"{split_label}: {len(flag_errors)} records have wrong 'correct' flags")

    # Build confusion matrix from details
    labels = sorted(set(d["true"] for d in details) | set(d["pred"] for d in details))
    confusion = defaultdict(lambda: defaultdict(int))
    for d in details:
        confusion[d["true"]][d["pred"]] += 1

    print(f"\n  Recalculated Confusion Matrix:")
    header_label = "Actual\\Pred"
    header = f"  {header_label:>14s}" + "".join(f"  {l:>12s}" for l in labels)
    print(header)
    for true_label in labels:
        row = f"  {true_label:>14s}"
        for pred_label in labels:
            row += f"  {confusion[true_label][pred_label]:>12d}"
        print(row)

    # Compare with reported confusion matrix
    if "confusion_matrix" in reported:
        reported_cm = reported["confusion_matrix"]
        for true_label in labels:
            for pred_label in labels:
                recalc_val = confusion[true_label][pred_label]
                reported_val = reported_cm.get(true_label, {}).get(pred_label, 0)
                if recalc_val != reported_val:
                    discrepancies.append(
                        f"{split_label}: CM[{true_label}][{pred_label}] reported={reported_val} recalc={recalc_val}"
                    )

    # Recalculate per-class precision, recall, F1
    print(f"\n  Recalculated Per-Class Metrics:")
    print(f"  {'Class':>14s}  {'Prec':>8s}  {'Recall':>8s}  {'F1':>8s}  {'Support':>8s}  |  {'R.Prec':>8s}  {'R.Recall':>8s}  {'R.F1':>8s}")

    macro_p_sum, macro_r_sum, macro_f1_sum = 0.0, 0.0, 0.0
    n_classes_with_support = 0

    for label in labels:
        support = sum(confusion[label][p] for p in labels)
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in labels if other != label)
        fn = sum(confusion[label][other] for other in labels if other != label)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        rpc = reported.get("per_class", {}).get(label, {})
        r_prec = rpc.get("precision", "N/A")
        r_recall = rpc.get("recall", "N/A")
        r_f1 = rpc.get("f1", "N/A")

        print(f"  {label:>14s}  {precision:>8.4f}  {recall:>8.4f}  {f1:>8.4f}  {support:>8d}  |  {str(r_prec):>8s}  {str(r_recall):>8s}  {str(r_f1):>8s}")

        if support > 0:
            macro_p_sum += precision
            macro_r_sum += recall
            macro_f1_sum += f1
            n_classes_with_support += 1

        if isinstance(r_prec, float) and abs(precision - r_prec) > 0.005:
            discrepancies.append(f"{split_label}: {label} precision reported={r_prec} recalc={precision:.4f}")
        if isinstance(r_recall, float) and abs(recall - r_recall) > 0.005:
            discrepancies.append(f"{split_label}: {label} recall reported={r_recall} recalc={recall:.4f}")
        if isinstance(r_f1, float) and abs(f1 - r_f1) > 0.005:
            discrepancies.append(f"{split_label}: {label} f1 reported={r_f1} recalc={f1:.4f}")

    macro_precision = macro_p_sum / n_classes_with_support if n_classes_with_support > 0 else 0.0
    macro_recall = macro_r_sum / n_classes_with_support if n_classes_with_support > 0 else 0.0
    macro_f1 = macro_f1_sum / n_classes_with_support if n_classes_with_support > 0 else 0.0

    print(f"\n  Recalculated Macro Metrics (over {n_classes_with_support} classes with support):")
    print(f"    Macro Precision: {macro_precision:.4f}  (reported: {reported.get('macro_precision', 'N/A')})")
    print(f"    Macro Recall:    {macro_recall:.4f}  (reported: {reported.get('macro_recall', 'N/A')})")
    print(f"    Macro F1:        {macro_f1:.4f}  (reported: {reported.get('macro_f1', 'N/A')})")

    if isinstance(reported.get('macro_precision'), (int, float)):
        if abs(macro_precision - reported['macro_precision']) > 0.005:
            discrepancies.append(f"{split_label}: macro_precision reported={reported['macro_precision']} recalc={macro_precision:.4f}")
    if isinstance(reported.get('macro_recall'), (int, float)):
        if abs(macro_recall - reported['macro_recall']) > 0.005:
            discrepancies.append(f"{split_label}: macro_recall reported={reported['macro_recall']} recalc={macro_recall:.4f}")
    if isinstance(reported.get('macro_f1'), (int, float)):
        if abs(macro_f1 - reported['macro_f1']) > 0.005:
            discrepancies.append(f"{split_label}: macro_f1 reported={reported['macro_f1']} recalc={macro_f1:.4f}")

    # List incorrect records
    incorrect = [d for d in details if not d["correct"]]
    if incorrect:
        print(f"\n  Misclassified Records ({len(incorrect)}):")
        for d in incorrect:
            print(f"    {d['id']}: true={d['true']} pred={d['pred']} conf={d['conf']} diff={d['diff']}")

# Also check: does the PHASE26 completion report cite metrics that differ from recalculated?
print("\n" + "=" * 72)
print("CROSS-REFERENCE: Completion Report vs Recalculated Test Set Metrics")
print("=" * 72)
test_lid = data["held_out_test_set_metrics"]["language_identification"]
print(f"  Reported test accuracy:        {test_lid['accuracy']}")
print(f"  Reported test macro_f1:        {test_lid['macro_f1']}")
print(f"  Reported test macro_precision: {test_lid['macro_precision']}")
print(f"  Reported test macro_recall:    {test_lid['macro_recall']}")
print(f"  Total correct:                 {test_lid['total_correct']}/{test_lid['total_records']}")

# Check the Phase 26 completion report narrative
# The session summary claimed: Tamil P=0.9524, but let's see if that matches
per_class = test_lid["per_class"]
print(f"\n  Per-class from PHASE26_TEST_RESULTS.json:")
for cls, metrics in per_class.items():
    print(f"    {cls}: P={metrics['precision']} R={metrics['recall']} F1={metrics['f1']} Support={metrics['support']}")

print("\n" + "=" * 72)
print("DISCREPANCY SUMMARY")
print("=" * 72)
if discrepancies:
    print(f"  Found {len(discrepancies)} discrepancies:")
    for d in discrepancies:
        print(f"    [DISCREPANCY] {d}")
else:
    print("  No discrepancies found between saved details and reported metrics.")

print()
sys.exit(0 if not discrepancies else 1)
