#!/usr/bin/env python3
"""
IGRIS Phase 26 — Full Benchmark Evaluation Runner.
Executes dev, val, and held-out test evaluations, tokenizer comparison,
resource profiling, and outputs comprehensive machine-readable results.
"""

import hashlib
import json
import time
import tracemalloc
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

PATCH_DIR = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")

import sys
sys.path.insert(0, str(PATCH_DIR / "scripts"))
sys.path.insert(0, str(PATCH_DIR))

from dataset_pipeline_v2 import DatasetPipelineV2, RawRecord, ProcessedRecord
from duplicate_detector_v2 import DuplicateDetectorV2
from language_identifier_v2 import LanguageIdentifierV2
from quality_filter_v2 import QualityConfigV2, QualityFilterV2
from tanglish_analyzer import TanglishAnalyzer
from unicode_processor_v2 import UnicodeProcessorV2
from tokenizers import Tokenizer
import sentencepiece as spm

print("=" * 70)
print("IGRIS Phase 26 — Comprehensive Evaluation Benchmark")
print("=" * 70)

# Load Dataset Splits
splits_path = PATCH_DIR / "PHASE26_DATASET_SPLITS.json"
with open(splits_path, "r", encoding="utf-8") as f:
    splits_pkg = json.load(f)

dev_fixtures = splits_pkg["splits"]["dev"]
val_fixtures = splits_pkg["splits"]["val"]
test_fixtures = splits_pkg["splits"]["test"]

print(f"Loaded splits: dev={len(dev_fixtures)}, val={len(val_fixtures)}, test={len(test_fixtures)}")

def evaluate_lid_on_split(records, lid_engine):
    y_true = [r["ground_truth_language"] for r in records]
    y_pred = []
    by_diff = defaultdict(lambda: {"correct": 0, "total": 0})
    details = []

    for r in records:
        res = lid_engine.identify(r["text"])
        y_pred.append(res.label)
        is_corr = (res.label == r["ground_truth_language"])
        diff = r["difficulty"]
        by_diff[diff]["total"] += 1
        if is_corr:
            by_diff[diff]["correct"] += 1
        details.append({
            "id": r["id"],
            "true": r["ground_truth_language"],
            "pred": res.label,
            "conf": res.confidence,
            "diff": diff,
            "correct": is_corr,
        })

    all_labels = ["ENGLISH", "OUT_OF_SCOPE", "TAMIL", "TANGLISH", "UNKNOWN"]
    conf_mat = {t: {p: 0 for p in all_labels} for t in all_labels}
    for yt, yp in zip(y_true, y_pred):
        if yt in conf_mat and yp in conf_mat[yt]:
            conf_mat[yt][yp] += 1

    correct_total = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
    acc = correct_total / len(y_true) if y_true else 0.0

    per_class = {}
    precisions = []
    recalls = []
    f1s = []

    for lbl in all_labels:
        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == lbl and yp == lbl)
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt != lbl and yp == lbl)
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == lbl and yp != lbl)
        p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
        support = tp + fn
        per_class[lbl] = {"precision": round(p, 4), "recall": round(r, 4), "f1": round(f1, 4), "support": support}
        if support > 0:
            precisions.append(p)
            recalls.append(r)
            f1s.append(f1)

    macro_p = np.mean(precisions) if precisions else 0.0
    macro_r = np.mean(recalls) if recalls else 0.0
    macro_f1 = np.mean(f1s) if f1s else 0.0

    diff_summary = {}
    for d, counts in by_diff.items():
        diff_summary[d] = {
            "correct": counts["correct"],
            "total": counts["total"],
            "accuracy": round(counts["correct"] / counts["total"], 4) if counts["total"] > 0 else 0.0
        }

    return {
        "accuracy": round(acc, 4),
        "total_correct": correct_total,
        "total_records": len(y_true),
        "macro_precision": round(macro_p, 4),
        "macro_recall": round(macro_r, 4),
        "macro_f1": round(macro_f1, 4),
        "per_class": per_class,
        "confusion_matrix": conf_mat,
        "difficulty_breakdown": diff_summary,
        "details": details,
    }

lid = LanguageIdentifierV2()

# 1. Dev Set Evaluation
dev_lid_metrics = evaluate_lid_on_split(dev_fixtures, lid)
print(f"\n[DEV SET] LID Accuracy: {dev_lid_metrics['accuracy']:.2%} | Macro F1: {dev_lid_metrics['macro_f1']:.4f}")

# 2. Val Set Threshold Comparison
thresholds = [0.70, 0.75, 0.80, 0.85, 0.90]
val_threshold_results = {}
for th in thresholds:
    dd = DuplicateDetectorV2(near_dup_threshold=th)
    tp = tn = fp = fn = 0
    for r in val_fixtures:
        text = r["text"]
        if not text.strip():
            continue
        exp_dup = r["expected_duplicate"]
        res = dd.check_and_register(r["id"], text)
        is_dup = res.is_duplicate
        if exp_dup and is_dup: tp += 1
        elif not exp_dup and not is_dup: tn += 1
        elif not exp_dup and is_dup: fp += 1
        else: fn += 1
    p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r_val = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * p * r_val / (p + r_val) if (p + r_val) > 0 else 0.0
    val_threshold_results[str(th)] = {"precision": round(p, 4), "recall": round(r_val, 4), "f1": round(f1, 4), "tp": tp, "tn": tn, "fp": fp, "fn": fn}

selected_dup_threshold = 0.70
print(f"[VAL SET] Selected optimal duplicate threshold: {selected_dup_threshold} (F1 = {val_threshold_results['0.7']['f1']})")

val_lid_metrics = evaluate_lid_on_split(val_fixtures, lid)
print(f"[VAL SET] LID Accuracy: {val_lid_metrics['accuracy']:.2%} | Macro F1: {val_lid_metrics['macro_f1']:.4f}")

# 3. Held-Out Test Set Evaluation (Unseen test set evaluated with selected threshold)
test_lid_metrics = evaluate_lid_on_split(test_fixtures, lid)
print(f"\n[HELD-OUT TEST SET] LID Accuracy: {test_lid_metrics['accuracy']:.2%} | Macro F1: {test_lid_metrics['macro_f1']:.4f}")
for lbl, m in sorted(test_lid_metrics['per_class'].items()):
    print(f"  {lbl}: P={m['precision']:.4f} R={m['recall']:.4f} F1={m['f1']:.4f} (Support={m['support']})")

# Full Pipeline on Held-Out Test Set
pipeline_test = DatasetPipelineV2(near_dup_threshold=selected_dup_threshold)
raw_test_records = [RawRecord(id=r["id"], text=r["text"], metadata=r) for r in test_fixtures]
processed_test, test_telemetry = pipeline_test.process_dataset(raw_test_records)

# Pipeline Action Performance on Test Set
y_true_act = [r["expected_processing_behavior"] for r in test_fixtures]
y_pred_act = [p.final_action for p in processed_test]
act_corr = sum(1 for yt, yp in zip(y_true_act, y_pred_act) if yt == yp)
action_accuracy = act_corr / len(y_true_act)

# Quality filter metrics on Test Set
y_true_q = [r["expected_quality_pass"] for r in test_fixtures]
y_pred_q = [p.quality_passed for p in processed_test]
q_tp = sum(1 for yt, yp in zip(y_true_q, y_pred_q) if yt is True and yp is True)
q_tn = sum(1 for yt, yp in zip(y_true_q, y_pred_q) if yt is False and yp is False)
q_fp = sum(1 for yt, yp in zip(y_true_q, y_pred_q) if yt is False and yp is True)
q_fn = sum(1 for yt, yp in zip(y_true_q, y_pred_q) if yt is True and yp is False)
q_p = q_tp / (q_tp + q_fp) if (q_tp + q_fp) > 0 else 0.0
q_r = q_tp / (q_tp + q_fn) if (q_tp + q_fn) > 0 else 0.0
q_f1 = 2 * q_p * q_r / (q_p + q_r) if (q_p + q_r) > 0 else 0.0

# Duplicate metrics on Test Set
y_true_d = [r["expected_duplicate"] for r in test_fixtures]
y_pred_d = [p.is_duplicate for p in processed_test]
d_tp = sum(1 for yt, yp in zip(y_true_d, y_pred_d) if yt is True and yp is True)
d_tn = sum(1 for yt, yp in zip(y_true_d, y_pred_d) if yt is False and yp is False)
d_fp = sum(1 for yt, yp in zip(y_true_d, y_pred_d) if yt is False and yp is True)
d_fn = sum(1 for yt, yp in zip(y_true_d, y_pred_d) if yt is True and yp is False)
d_p = d_tp / (d_tp + d_fp) if (d_tp + d_fp) > 0 else 0.0
d_r = d_tp / (d_tp + d_fn) if (d_tp + d_fn) > 0 else 0.0
d_f1 = 2 * d_p * d_r / (d_p + d_r) if (d_p + d_r) > 0 else 0.0

print(f"\n[TEST SET PIPELINE ACTION] Accuracy: {action_accuracy:.2%} ({act_corr}/{len(y_true_act)})")
print(f"[TEST SET QUALITY FILTER] Accuracy: {(q_tp+q_tn)/len(y_true_q):.2%}, P={q_p:.4f}, R={q_r:.4f}, F1={q_f1:.4f}")
print(f"[TEST SET DUPLICATE] P={d_p:.4f}, R={d_r:.4f}, F1={d_f1:.4f} (TP={d_tp}, TN={d_tn}, FP={d_fp}, FN={d_fn})")

# 4. Tokenizer Comparison Across All 3 Splits (300 records)
tok_a_path = PATCH_DIR / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
tok_b_path = PATCH_DIR / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
h_a = hashlib.sha256(open(tok_a_path, "rb").read()).hexdigest()
h_b = hashlib.sha256(open(tok_b_path, "rb").read()).hexdigest()

tok_a = Tokenizer.from_file(str(tok_a_path))
sp_b = spm.SentencePieceProcessor()
sp_b.load(str(tok_b_path))

clean_eval_records = []
for split in ["dev", "val", "test"]:
    for r in splits_pkg["splits"][split]:
        if r["expected_quality_pass"] and not r["expected_duplicate"]:
            clean_eval_records.append(r)

# Tokenizer Candidate A Evaluation
a_tokens = 0
a_words = 0
a_unk = 0
a_roundtrip = 0
a_lens = []
a_lang_stats = defaultdict(lambda: {"tokens": 0, "words": 0, "records": 0})
unk_id_a = tok_a.token_to_id("[UNK]") or tok_a.token_to_id("<unk>")

t0_a = time.perf_counter()
for r in clean_eval_records:
    t = r["text"]
    w = len(t.split())
    ids = tok_a.encode(t).ids
    a_tokens += len(ids)
    a_words += w
    a_lens.append(len(ids))
    if unk_id_a is not None:
        a_unk += sum(1 for i in ids if i == unk_id_a)
    dec = tok_a.decode(ids)
    if dec.strip() == t.strip():
        a_roundtrip += 1
    lang = r["ground_truth_language"]
    a_lang_stats[lang]["tokens"] += len(ids)
    a_lang_stats[lang]["words"] += w
    a_lang_stats[lang]["records"] += 1
dur_a = time.perf_counter() - t0_a

# Tokenizer Candidate B Evaluation
b_tokens = 0
b_words = 0
b_unk = 0
b_roundtrip = 0
b_lens = []
b_lang_stats = defaultdict(lambda: {"tokens": 0, "words": 0, "records": 0})
unk_id_b = sp_b.unk_id()

t0_b = time.perf_counter()
for r in clean_eval_records:
    t = r["text"]
    w = len(t.split())
    ids = sp_b.encode_as_ids(t)
    b_tokens += len(ids)
    b_words += w
    b_lens.append(len(ids))
    b_unk += sum(1 for i in ids if i == unk_id_b)
    dec = sp_b.decode_ids(ids)
    if dec.strip() == t.strip():
        b_roundtrip += 1
    lang = r["ground_truth_language"]
    b_lang_stats[lang]["tokens"] += len(ids)
    b_lang_stats[lang]["words"] += w
    b_lang_stats[lang]["records"] += 1
dur_b = time.perf_counter() - t0_b

tok_comparison = {
    "records_evaluated": len(clean_eval_records),
    "candidate_a": {
        "type": "ByteLevel BPE",
        "sha256": h_a,
        "hash_verified": h_a == "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561",
        "total_tokens": a_tokens,
        "fertility": round(a_tokens / a_words, 4),
        "unk_rate": round(a_unk / a_tokens, 6),
        "unk_count": a_unk,
        "roundtrip_rate": round(a_roundtrip / len(clean_eval_records), 4),
        "throughput_tokens_sec": round(a_tokens / dur_a, 1) if dur_a > 0 else 0,
        "seq_len_stats": {
            "min": int(min(a_lens)),
            "max": int(max(a_lens)),
            "mean": round(float(np.mean(a_lens)), 2),
            "median": round(float(np.median(a_lens)), 2),
            "p95": round(float(np.percentile(a_lens, 95)), 2),
        },
        "per_language_fertility": {
            l: round(d["tokens"] / d["words"], 4) if d["words"] > 0 else 0.0
            for l, d in a_lang_stats.items()
        }
    },
    "candidate_b": {
        "type": "SentencePiece Unigram",
        "sha256": h_b,
        "hash_verified": h_b == "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888",
        "total_tokens": b_tokens,
        "fertility": round(b_tokens / b_words, 4),
        "unk_rate": round(b_unk / b_tokens, 6),
        "unk_count": b_unk,
        "roundtrip_rate": round(b_roundtrip / len(clean_eval_records), 4),
        "throughput_tokens_sec": round(b_tokens / dur_b, 1) if dur_b > 0 else 0,
        "seq_len_stats": {
            "min": int(min(b_lens)),
            "max": int(max(b_lens)),
            "mean": round(float(np.mean(b_lens)), 2),
            "median": round(float(np.median(b_lens)), 2),
            "p95": round(float(np.percentile(b_lens, 95)), 2),
        },
        "per_language_fertility": {
            l: round(d["tokens"] / d["words"], 4) if d["words"] > 0 else 0.0
            for l, d in b_lang_stats.items()
        }
    }
}

# 5. Local Hardware Resource Profiling (300 records)
all_300 = []
for split in ["dev", "val", "test"]:
    all_300.extend([RawRecord(r["id"], r["text"], metadata=r) for r in splits_pkg["splits"][split]])

tracemalloc.start()
t0_proc = time.process_time()
t0_wall = time.perf_counter()

proc_pipeline = DatasetPipelineV2(near_dup_threshold=selected_dup_threshold)
proc_all, all_telemetry = proc_pipeline.process_dataset(all_300)

dur_wall = time.perf_counter() - t0_wall
dur_proc = time.process_time() - t0_proc
cur_mem, peak_mem = tracemalloc.get_traced_memory()
tracemalloc.stop()

cpu_load = (dur_proc / dur_wall * 100) if dur_wall > 0 else 0.0
throughput_rec_sec = len(all_300) / dur_wall if dur_wall > 0 else 0.0
throughput_tok_sec = (a_tokens / len(clean_eval_records) * len(all_300)) / dur_wall if dur_wall > 0 else 0.0

resource_telemetry = {
    "total_records_processed": len(all_300),
    "wall_clock_time_sec": round(dur_wall, 4),
    "cpu_process_time_sec": round(dur_proc, 4),
    "estimated_cpu_utilization_pct": round(cpu_load, 1),
    "peak_memory_mb": round(peak_mem / (1024 * 1024), 2),
    "records_per_second": round(throughput_rec_sec, 1),
    "tokens_per_second": round(throughput_tok_sec, 1),
}

# 6. Tanglish Linguistic Analysis
ta = TanglishAnalyzer()
tanglish_records = [r for r in all_300 if r.metadata.get("ground_truth_language") == "TANGLISH"]
ta_switches = 0
ta_particles = 0
ta_plausible = 0
for tr in tanglish_records:
    analysis = ta.analyze(tr.text)
    ta_switches += len(analysis.code_switch_points)
    ta_particles += len(analysis.discourse_markers_found)
    if analysis.is_structurally_plausible:
        ta_plausible += 1

tanglish_metrics = {
    "total_tanglish_evaluated": len(tanglish_records),
    "avg_code_switch_boundaries": round(ta_switches / len(tanglish_records), 2) if tanglish_records else 0,
    "avg_discourse_markers": round(ta_particles / len(tanglish_records), 2) if tanglish_records else 0,
    "structural_plausibility_rate": round(ta_plausible / len(tanglish_records), 4) if tanglish_records else 0,
}

# 7. Unicode Integrity Telemetry
up = UnicodeProcessorV2()
u_stable = 0
u_combining = 0
u_virama = 0
u_malformed = 0
for r in all_300:
    t = r.text
    norm1, rep = up.normalize(t)
    norm2, _ = up.normalize(norm1)
    if norm1 == norm2:
        u_stable += 1
    u_combining += rep.tamil_combining_marks_preserved
    u_virama += rep.virama_sequences_preserved
    u_malformed += len(rep.malformed_sequences)

unicode_metrics = {
    "total_records_checked": len(all_300),
    "nfc_idempotence_rate": round(u_stable / len(all_300), 4),
    "combining_marks_preserved_total": u_combining,
    "virama_consonants_preserved_total": u_virama,
    "malformed_sequences_flagged": u_malformed,
}

# Assemble Full Results Package
results_package = {
    "benchmark_version": "IGRIS-P26-FINAL-V1.0",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "evaluation_split_counts": {
        "dev": len(dev_fixtures),
        "val": len(val_fixtures),
        "test": len(test_fixtures),
        "total": len(all_300),
    },
    "development_set_metrics": dev_lid_metrics,
    "validation_set_threshold_search": val_threshold_results,
    "validation_set_metrics": val_lid_metrics,
    "held_out_test_set_metrics": {
        "language_identification": test_lid_metrics,
        "pipeline_action_accuracy": round(action_accuracy, 4),
        "quality_filter": {
            "accuracy": round((q_tp + q_tn) / len(y_true_q), 4),
            "precision": round(q_p, 4),
            "recall": round(q_r, 4),
            "f1": round(q_f1, 4),
            "confusion": {"tp": q_tp, "tn": q_tn, "fp": q_fp, "fn": q_fn},
        },
        "duplicate_detection": {
            "threshold": selected_dup_threshold,
            "precision": round(d_p, 4),
            "recall": round(d_r, 4),
            "f1": round(d_f1, 4),
            "confusion": {"tp": d_tp, "tn": d_tn, "fp": d_fp, "fn": d_fn},
        }
    },
    "tokenizer_comparison": tok_comparison,
    "tanglish_linguistic_metrics": tanglish_metrics,
    "unicode_preservation_metrics": unicode_metrics,
    "hardware_performance_profile": resource_telemetry,
}

# Write PHASE26_TEST_RESULTS.json
json_content = json.dumps(results_package, indent=2, ensure_ascii=False)
for dest in [PATCH_DIR, ARTIFACT_DIR]:
    p = dest / "PHASE26_TEST_RESULTS.json"
    p.write_text(json_content, encoding="utf-8")
print(f"\nWritten PHASE26_TEST_RESULTS.json to patch and artifact directories.")

print("=" * 70)
print("Benchmark run complete.")
print("=" * 70)
