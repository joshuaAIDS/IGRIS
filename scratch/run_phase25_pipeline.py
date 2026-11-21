#!/usr/bin/env python3
"""
IGRIS Phase 25 — Full End-to-End Synthetic Pipeline Runner and Validator.
Executes the pipeline, validates all criteria, verifies tokenizers, and dumps evaluation JSON.
"""

import hashlib
import json
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

PATCH_DIR = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
sys.path.insert(0, str(PATCH_DIR / "scripts"))
sys.path.insert(0, str(PATCH_DIR))

from dataset_pipeline_v2 import DatasetPipelineV2, RawRecord, ProcessedRecord
from duplicate_detector_v2 import DuplicateDetectorV2
from language_identifier_v2 import LanguageIdentifierV2
from quality_filter_v2 import QualityConfigV2, QualityFilterV2
from tanglish_analyzer import TanglishAnalyzer
from unicode_processor_v2 import UnicodeProcessorV2

ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")

print("=" * 70)
print("IGRIS Phase 25 — End-to-End Synthetic Pipeline Validation")
print("=" * 70)

# Step 1: Load Benchmark Fixtures
fixtures_path = PATCH_DIR / "PHASE25_SYNTHETIC_BENCHMARK_FIXTURES.jsonl"
fixtures = []
with open(fixtures_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            fixtures.append(json.loads(line))

print(f"Loaded {len(fixtures)} synthetic benchmark fixtures.")

raw_records = [
    RawRecord(
        id=f["id"],
        text=f["text"],
        source_id="SYNTHETIC_BENCHMARK_P25",
        metadata={
            "ground_truth_language": f["ground_truth_language"],
            "category": f["category"],
            "expected_quality_pass": f["expected_quality_pass"],
            "expected_duplicate": f["expected_duplicate"],
            "expected_action": f["expected_action"],
            "expected_rejection_reasons": f["expected_rejection_reasons"],
            "notes": f.get("notes", ""),
        }
    )
    for f in fixtures
]

# Step 2: Execute Pipeline Run 1
pipeline = DatasetPipelineV2(near_dup_threshold=0.80)
processed_run1, telemetry_run1 = pipeline.process_dataset(raw_records)
print(f"Pipeline Run 1 completed in {telemetry_run1['pipeline_elapsed_sec']}s")
print(f"Actions: {telemetry_run1['action_counts']}")
print(f"Languages: {telemetry_run1['language_distribution']}")

# Step 3: Reproducibility Test (Run 2 with reset state)
pipeline.reset_state()
processed_run2, telemetry_run2 = pipeline.process_dataset(raw_records)

# Verify bit-for-bit determinism (ignoring runtime timestamp differences)
determinism_mismatches = []
for r1, r2 in zip(processed_run1, processed_run2):
    d1 = r1.to_dict()
    d2 = r2.to_dict()
    # strip timestamp for comparison
    d1.pop("timestamp_utc", None)
    d2.pop("timestamp_utc", None)
    if d1 != d2:
        determinism_mismatches.append((r1.id, "Mismatch between Run 1 and Run 2"))

reproducibility_passed = len(determinism_mismatches) == 0
print(f"Reproducibility determinism check: {'PASSED' if reproducibility_passed else 'FAILED'} ({len(determinism_mismatches)} mismatches)")

# Step 4: Language Classification Evaluation
y_true_lang = [r.metadata["ground_truth_language"] for r in raw_records]
y_pred_lang = [p.language_label for p in processed_run1]

all_labels = sorted(list(set(y_true_lang + y_pred_lang)))
lang_confusion = {t: {p: 0 for p in all_labels} for t in all_labels}
for yt, yp in zip(y_true_lang, y_pred_lang):
    lang_confusion[yt][yp] += 1

lang_correct = sum(1 for yt, yp in zip(y_true_lang, y_pred_lang) if yt == yp)
lang_accuracy = lang_correct / len(y_true_lang)

per_class_lang = {}
for lbl in all_labels:
    tp = sum(1 for yt, yp in zip(y_true_lang, y_pred_lang) if yt == lbl and yp == lbl)
    fp = sum(1 for yt, yp in zip(y_true_lang, y_pred_lang) if yt != lbl and yp == lbl)
    fn = sum(1 for yt, yp in zip(y_true_lang, y_pred_lang) if yt == lbl and yp != lbl)
    p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    per_class_lang[lbl] = {
        "precision": round(p, 4),
        "recall": round(r, 4),
        "f1": round(f1, 4),
        "tp": tp, "fp": fp, "fn": fn,
        "support": tp + fn,
    }

print(f"\nLanguage Identification Accuracy: {lang_accuracy:.2%} ({lang_correct}/{len(y_true_lang)})")
for lbl, m in sorted(per_class_lang.items()):
    print(f"  {lbl}: P={m['precision']:.4f} R={m['recall']:.4f} F1={m['f1']:.4f} (Support={m['support']})")

# Step 5: Unicode Processing Validation
unicode_nfc_stability_failures = 0
combining_marks_preserved_total = sum(p.tamil_combining_preserved for p in processed_run1)
virama_preserved_total = sum(p.virama_preserved for p in processed_run1)
zwj_zwnj_preserved_total = sum(p.zwj_zwnj_preserved for p in processed_run1)
malformed_detected_count = sum(len(p.unicode_malformed_sequences) for p in processed_run1)

for p in processed_run1:
    # Verify round trip normalization stability: normalize(norm) == norm
    n2, _ = pipeline.unicode_proc.normalize(p.normalized_text)
    if n2 != p.normalized_text:
        unicode_nfc_stability_failures += 1

print(f"\nUnicode Processing:")
print(f"  NFC stability failures: {unicode_nfc_stability_failures}")
print(f"  Tamil combining marks preserved: {combining_marks_preserved_total}")
print(f"  Virama sequences preserved: {virama_preserved_total}")
print(f"  ZWJ/ZWNJ sequences preserved: {zwj_zwnj_preserved_total}")
print(f"  Malformed sequences detected: {malformed_detected_count}")

# Step 6: Quality Filter Validation
y_true_q = [r.metadata["expected_quality_pass"] for r in raw_records]
y_pred_q = [p.quality_passed for p in processed_run1]

q_tp = sum(1 for yt, yp in zip(y_true_q, y_pred_q) if yt is True and yp is True)
q_tn = sum(1 for yt, yp in zip(y_true_q, y_pred_q) if yt is False and yp is False)
q_fp = sum(1 for yt, yp in zip(y_true_q, y_pred_q) if yt is False and yp is True)
q_fn = sum(1 for yt, yp in zip(y_true_q, y_pred_q) if yt is True and yp is False)
q_precision = q_tp / (q_tp + q_fp) if (q_tp + q_fp) > 0 else 0.0
q_recall = q_tp / (q_tp + q_fn) if (q_tp + q_fn) > 0 else 0.0
q_f1 = 2 * q_precision * q_recall / (q_precision + q_recall) if (q_precision + q_recall) > 0 else 0.0
q_accuracy = (q_tp + q_tn) / len(y_true_q)

print(f"\nQuality Filter Performance:")
print(f"  Accuracy: {q_accuracy:.2%} (TP={q_tp}, TN={q_tn}, FP={q_fp}, FN={q_fn})")
print(f"  Precision: {q_precision:.4f}, Recall: {q_recall:.4f}, F1: {q_f1:.4f}")

# Step 7: Duplicate Detection Validation
y_true_dup = [r.metadata["expected_duplicate"] for r in raw_records]
y_pred_dup = [p.is_duplicate for p in processed_run1]

dup_tp = sum(1 for yt, yp in zip(y_true_dup, y_pred_dup) if yt is True and yp is True)
dup_tn = sum(1 for yt, yp in zip(y_true_dup, y_pred_dup) if yt is False and yp is False)
dup_fp = sum(1 for yt, yp in zip(y_true_dup, y_pred_dup) if yt is False and yp is True)
dup_fn = sum(1 for yt, yp in zip(y_true_dup, y_pred_dup) if yt is True and yp is False)
dup_precision = dup_tp / (dup_tp + dup_fp) if (dup_tp + dup_fp) > 0 else 0.0
dup_recall = dup_tp / (dup_tp + dup_fn) if (dup_tp + dup_fn) > 0 else 0.0
dup_f1 = 2 * dup_precision * dup_recall / (dup_precision + dup_recall) if (dup_precision + dup_recall) > 0 else 0.0

print(f"\nDuplicate Detection Performance:")
print(f"  Precision: {dup_precision:.4f}, Recall: {dup_recall:.4f}, F1: {dup_f1:.4f}")
print(f"  TP={dup_tp}, TN={dup_tn}, FP={dup_fp}, FN={dup_fn}")

# Step 8: Action Decision Validation
y_true_act = [r.metadata["expected_action"] for r in raw_records]
y_pred_act = [p.final_action for p in processed_run1]
action_correct = sum(1 for yt, yp in zip(y_true_act, y_pred_act) if yt == yp)
action_accuracy = action_correct / len(y_true_act)
print(f"\nPipeline Classification Action Accuracy: {action_accuracy:.2%} ({action_correct}/{len(y_true_act)})")

# Step 9: Tokenizer Candidate A & B Hash and Read-Only Evaluation
tok_a_path = PATCH_DIR / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
tok_b_path = PATCH_DIR / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"

tok_a_hash = hashlib.sha256(open(tok_a_path, "rb").read()).hexdigest()
tok_b_hash = hashlib.sha256(open(tok_b_path, "rb").read()).hexdigest()

expected_tok_a_hash = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
expected_tok_b_hash = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

tok_a_match = tok_a_hash == expected_tok_a_hash
tok_b_match = tok_b_hash == expected_tok_b_hash

print(f"\nTokenizer Verification:")
print(f"  Candidate A Hash: {tok_a_hash[:16]}... Match: {tok_a_match}")
print(f"  Candidate B Hash: {tok_b_hash[:16]}... Match: {tok_b_match}")

# Evaluate Candidate A Tokenizer on Accepted Records
from tokenizers import Tokenizer
tok_a = Tokenizer.from_file(str(tok_a_path))
unk_id = tok_a.token_to_id("[UNK]")
if unk_id is None:
    unk_id = tok_a.token_to_id("<unk>")

accepted_records = [p for p in processed_run1 if p.final_action == "ACCEPTED"]
total_tokens = 0
total_words = 0
total_unk = 0
roundtrip_pass = 0

lang_fertility = defaultdict(lambda: {"tokens": 0, "words": 0, "unk": 0, "count": 0})

for rec in accepted_records:
    enc = tok_a.encode(rec.normalized_text)
    ids = enc.ids
    w_count = len(rec.normalized_text.split())
    u_count = sum(1 for i in ids if i == unk_id) if unk_id is not None else 0
    total_tokens += len(ids)
    total_words += w_count
    total_unk += u_count
    
    # decode check
    dec = tok_a.decode(ids)
    if dec.strip() == rec.normalized_text.strip():
        roundtrip_pass += 1

    lf = lang_fertility[rec.language_label]
    lf["tokens"] += len(ids)
    lf["words"] += w_count
    lf["unk"] += u_count
    lf["count"] += 1

overall_fertility = total_tokens / total_words if total_words > 0 else 0.0
overall_unk_rate = total_unk / total_tokens if total_tokens > 0 else 0.0
roundtrip_rate = roundtrip_pass / len(accepted_records) if accepted_records else 0.0

print(f"\nTokenizer Candidate A Evaluation on {len(accepted_records)} Accepted Records:")
print(f"  Overall Fertility: {overall_fertility:.4f} tokens/word")
print(f"  Overall UNK Rate: {overall_unk_rate:.6f} ({total_unk}/{total_tokens})")
print(f"  Lossless Roundtrip: {roundtrip_pass}/{len(accepted_records)} ({roundtrip_rate:.2%})")
for l, fd in sorted(lang_fertility.items()):
    fert = fd["tokens"] / fd["words"] if fd["words"] > 0 else 0.0
    print(f"    {l} ({fd['count']} docs): fertility={fert:.4f}, tokens={fd['tokens']}, unk={fd['unk']}")

# Compile Test Results Structure
test_results_data = {
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "pipeline_version": "IGRIS-P25-V2.0",
    "total_benchmark_records": len(fixtures),
    "reproducibility": {
        "passed": reproducibility_passed,
        "mismatches": len(determinism_mismatches),
    },
    "language_identification": {
        "overall_accuracy": round(lang_accuracy, 4),
        "total_correct": lang_correct,
        "total_evaluated": len(y_true_lang),
        "confusion_matrix": lang_confusion,
        "per_class_metrics": per_class_lang,
        "phase24_baseline_accuracy": 0.8800,
        "phase25_accuracy": round(lang_accuracy, 4),
        "delta_improvement": round(lang_accuracy - 0.8800, 4),
    },
    "unicode_processing": {
        "nfc_stability_failures": unicode_nfc_stability_failures,
        "combining_marks_preserved": combining_marks_preserved_total,
        "virama_preserved": virama_preserved_total,
        "zwj_zwnj_preserved": zwj_zwnj_preserved_total,
        "malformed_sequences_detected": malformed_detected_count,
    },
    "quality_filter": {
        "accuracy": round(q_accuracy, 4),
        "precision": round(q_precision, 4),
        "recall": round(q_recall, 4),
        "f1": round(q_f1, 4),
        "confusion": {"tp": q_tp, "tn": q_tn, "fp": q_fp, "fn": q_fn},
    },
    "duplicate_detection": {
        "precision": round(dup_precision, 4),
        "recall": round(dup_recall, 4),
        "f1": round(dup_f1, 4),
        "confusion": {"tp": dup_tp, "tn": dup_tn, "fp": dup_fp, "fn": dup_fn},
    },
    "pipeline_classification": {
        "action_accuracy": round(action_accuracy, 4),
        "action_counts": telemetry_run1["action_counts"],
        "rejection_reasons_distribution": telemetry_run1["rejection_reasons_distribution"],
    },
    "tokenizer_evaluation": {
        "candidate_a_hash": tok_a_hash,
        "candidate_a_match": tok_a_match,
        "candidate_b_hash": tok_b_hash,
        "candidate_b_match": tok_b_match,
        "accepted_records_evaluated": len(accepted_records),
        "overall_fertility": round(overall_fertility, 4),
        "overall_unk_rate": round(overall_unk_rate, 6),
        "roundtrip_lossless_rate": round(roundtrip_rate, 4),
        "per_language_fertility": {
            l: {
                "fertility": round(fd["tokens"] / fd["words"], 4) if fd["words"] > 0 else 0.0,
                "tokens": fd["tokens"],
                "words": fd["words"],
                "unk": fd["unk"],
                "records": fd["count"],
            }
            for l, fd in lang_fertility.items()
        }
    }
}

# Write PHASE25_TEST_RESULTS.json
test_results_json = json.dumps(test_results_data, indent=2, ensure_ascii=False)
for dest in [PATCH_DIR, ARTIFACT_DIR]:
    p = dest / "PHASE25_TEST_RESULTS.json"
    p.write_text(test_results_json, encoding="utf-8")
print(f"Written PHASE25_TEST_RESULTS.json to patch and artifact directories.")

# Write PHASE25_SYNTHETIC_DATASET_MANIFEST.json
manifest_data = {
    "manifest_version": "1.0",
    "generation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "pipeline_config": {
        "near_dup_threshold": 0.80,
        "min_language_confidence": 0.35,
        "quality_filter_min_chars": 10,
        "quality_filter_min_words": 2,
    },
    "summary_telemetry": telemetry_run1,
    "records": [p.to_dict() for p in processed_run1],
}

manifest_json = json.dumps(manifest_data, indent=2, ensure_ascii=False)
for dest in [PATCH_DIR, ARTIFACT_DIR]:
    p = dest / "PHASE25_SYNTHETIC_DATASET_MANIFEST.json"
    p.write_text(manifest_json, encoding="utf-8")
print(f"Written PHASE25_SYNTHETIC_DATASET_MANIFEST.json ({len(processed_run1)} records).")

print("=" * 70)
print("Pipeline run and evaluation complete.")
print("=" * 70)
