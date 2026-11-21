"""
scratch/run_generalization_evaluation.py

Evaluates Original Candidate A vs Experimental Candidate A across
the 3,000 independent synthetic records. Generates:
- TOKENIZER_GENERALIZATION_METRICS.csv
- TOKENIZER_CATEGORY_BREAKDOWN.csv
- TOKENIZER_SCRIPT_GENERALIZATION.csv
- Detailed benchmark speed & roundtrip results
"""

import csv
import hashlib
import json
import math
import os
import platform
import statistics
import sys
import time
import unicodedata
from collections import Counter
from pathlib import Path
from tokenizers import Tokenizer

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\e52ff414-ecc8-4b21-888c-82066c8980e0")

ORIGINAL_CAND_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
EXPECTED_EXP_HASH = "3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce"

STRUCTURAL_TOKENS = [
    (0, "<|pad|>"),
    (1, "<|begin_of_text|>"),
    (2, "<|end_of_text|>"),
    (3, "<think>"),
    (4, "</think>"),
    (5, "<action>"),
    (6, "</action>"),
    (7, "<action_result>"),
    (8, "</action_result>"),
    (9, "<|system|>"),
    (10, "<|user|>"),
    (11, "<|assistant|>")
]

def percentile(vals, p):
    if not vals:
        return 0.0
    sorted_vals = sorted(vals)
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(sorted_vals[int(k)])
    d0 = sorted_vals[int(f)] * (c - k)
    d1 = sorted_vals[int(c)] * (k - f)
    return float(d0 + d1)

def compute_sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    print("=" * 80)
    print("EVALUATING TOKENIZER GENERALIZATION ACROSS 3,000 INDEPENDENT RECORDS")
    print("=" * 80)

    # 1. Verify Hashes
    cand_a_path = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    cand_exp_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"

    hash_a = compute_sha256(cand_a_path)
    hash_exp = compute_sha256(cand_exp_path)
    assert hash_a == ORIGINAL_CAND_A_HASH, f"Cand A hash violation: {hash_a}"
    assert hash_exp == EXPECTED_EXP_HASH, f"Cand Exp hash violation: {hash_exp}"
    print("[PASS] Tokenizer artifact hashes strictly verified.")

    # 2. Load tokenizers
    tok_a = Tokenizer.from_file(str(cand_a_path))
    tok_exp = Tokenizer.from_file(str(cand_exp_path))

    # Verify structural tokens
    for expected_id, expected_tok in STRUCTURAL_TOKENS:
        act_a = tok_a.id_to_token(expected_id)
        act_exp = tok_exp.id_to_token(expected_id)
        assert act_a == expected_tok, f"Cand A structural mismatch: {act_a} != {expected_tok}"
        assert act_exp == expected_tok, f"Cand Exp structural mismatch: {act_exp} != {expected_tok}"
    print("[PASS] Structural special tokens (IDs 0-11) verified in both tokenizers.")

    # 3. Load 3,000 records
    manifest_path = WORKSPACE_ROOT / "INDEPENDENT_SYNTHETIC_CORPUS_MANIFEST.csv"
    with open(manifest_path, encoding="utf-8") as f:
        records = list(csv.DictReader(f))
    assert len(records) == 3000, f"Expected 3000 records, got {len(records)}"
    print(f"Loaded {len(records)} independent synthetic records from manifest.")

    for r in records:
        r["word_count"] = int(r["word_count"])
        r["char_count"] = int(r["char_count"])

    # Helper evaluation function
    def evaluate_group(subset, group_name):
        rec_count = len(subset)
        words_total = sum(r["word_count"] for r in subset)
        chars_total = sum(r["char_count"] for r in subset)

        lens_a, lens_exp = [], []
        fert_word_a, fert_word_exp = [], []
        fert_char_a, fert_char_exp = [], []
        vocab_a = set()
        vocab_exp = set()

        roundtrip_a_pass = 0
        roundtrip_exp_pass = 0

        for r in subset:
            txt = r["text"]
            enc_a = tok_a.encode(txt)
            enc_exp = tok_exp.encode(txt)

            ids_a = enc_a.ids
            ids_exp = enc_exp.ids

            lens_a.append(len(ids_a))
            lens_exp.append(len(ids_exp))

            vocab_a.update(ids_a)
            vocab_exp.update(ids_exp)

            w = max(1, r["word_count"])
            c = max(1, r["char_count"])

            fert_word_a.append(len(ids_a) / w)
            fert_word_exp.append(len(ids_exp) / w)

            fert_char_a.append(len(ids_a) / c)
            fert_char_exp.append(len(ids_exp) / c)

            # Round trip test
            dec_a = tok_a.decode(ids_a)
            dec_exp = tok_exp.decode(ids_exp)
            if dec_a == txt:
                roundtrip_a_pass += 1
            if dec_exp == txt:
                roundtrip_exp_pass += 1

        total_toks_a = sum(lens_a)
        total_toks_exp = sum(lens_exp)
        reduction_pct = ((total_toks_a - total_toks_exp) / total_toks_a) * 100.0 if total_toks_a else 0.0

        return {
            "subset_name": group_name,
            "record_count": rec_count,
            "words_total": words_total,
            "chars_total": chars_total,
            "cand_a_total_tokens": total_toks_a,
            "cand_a_fertility_per_word": round(total_toks_a / words_total, 4) if words_total else 0.0,
            "cand_a_fertility_per_char": round(total_toks_a / chars_total, 4) if chars_total else 0.0,
            "cand_a_seq_len_median": round(statistics.median(lens_a), 2),
            "cand_a_seq_len_p90": round(percentile(lens_a, 90), 2),
            "cand_a_seq_len_p95": round(percentile(lens_a, 95), 2),
            "cand_a_seq_len_max": max(lens_a),
            "cand_a_active_vocab_count": len(vocab_a),
            "cand_a_active_vocab_pct": round((len(vocab_a) / 32768) * 100.0, 4),
            "cand_a_roundtrip_accuracy": round((roundtrip_a_pass / rec_count) * 100.0, 2),
            "cand_exp_total_tokens": total_toks_exp,
            "cand_exp_fertility_per_word": round(total_toks_exp / words_total, 4) if words_total else 0.0,
            "cand_exp_fertility_per_char": round(total_toks_exp / chars_total, 4) if chars_total else 0.0,
            "cand_exp_seq_len_median": round(statistics.median(lens_exp), 2),
            "cand_exp_seq_len_p90": round(percentile(lens_exp, 90), 2),
            "cand_exp_seq_len_p95": round(percentile(lens_exp, 95), 2),
            "cand_exp_seq_len_max": max(lens_exp),
            "cand_exp_active_vocab_count": len(vocab_exp),
            "cand_exp_active_vocab_pct": round((len(vocab_exp) / 32768) * 100.0, 4),
            "cand_exp_roundtrip_accuracy": round((roundtrip_exp_pass / rec_count) * 100.0, 2),
            "token_reduction_pct": round(reduction_pct, 2)
        }

    # 4. Compute Metrics across Partitions
    csv_fields = [
        "subset_name", "record_count", "words_total", "chars_total",
        "cand_a_total_tokens", "cand_a_fertility_per_word", "cand_a_fertility_per_char",
        "cand_a_seq_len_median", "cand_a_seq_len_p90", "cand_a_seq_len_p95", "cand_a_seq_len_max",
        "cand_a_active_vocab_count", "cand_a_active_vocab_pct", "cand_a_roundtrip_accuracy",
        "cand_exp_total_tokens", "cand_exp_fertility_per_word", "cand_exp_fertility_per_char",
        "cand_exp_seq_len_median", "cand_exp_seq_len_p90", "cand_exp_seq_len_p95", "cand_exp_seq_len_max",
        "cand_exp_active_vocab_count", "cand_exp_active_vocab_pct", "cand_exp_roundtrip_accuracy",
        "token_reduction_pct"
    ]

    print("Computing metrics across Generalization partitions...")
    # Overall and Language Breakdown
    metrics_rows = [
        evaluate_group(records, "FULL_INDEPENDENT_CORPUS"),
        evaluate_group([r for r in records if r["language"] == "TAMIL"], "LANGUAGE_TAMIL"),
        evaluate_group([r for r in records if r["language"] == "ENGLISH"], "LANGUAGE_ENGLISH"),
        evaluate_group([r for r in records if r["language"] == "TANGLISH"], "LANGUAGE_TANGLISH"),
    ]

    # Category Breakdown
    category_order = ["conversational", "formal", "educational", "technical", "long_form"]
    cat_rows = []
    for cat in category_order:
        cat_rows.append(evaluate_group([r for r in records if r["category"] == cat], f"CATEGORY_{cat.upper()}"))
    for cat in category_order:
        for lang in ["TAMIL", "ENGLISH", "TANGLISH"]:
            cat_rows.append(evaluate_group([r for r in records if r["category"] == cat and r["language"] == lang], f"{lang}_{cat.upper()}"))

    # Script Breakdown
    script_order = ["TAMIL_SCRIPT", "LATIN_SCRIPT", "MIXED_SCRIPT"]
    script_rows = [evaluate_group([r for r in records if r["script_form"] == s], f"SCRIPT_{s}") for s in script_order]

    # Save CSVs
    def write_csv_multi(filename, rows):
        targets = [
            WORKSPACE_ROOT / filename,
            WORKSPACE_ROOT / "documentation" / filename,
            PATCH_ROOT / filename,
            ARTIFACT_DIR / filename
        ]
        for t in targets:
            t.parent.mkdir(parents=True, exist_ok=True)
            with open(t, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=csv_fields)
                w.writeheader()
                w.writerows(rows)
            print(f"Saved {filename} to {t} ({len(rows)} rows)")

    write_csv_multi("TOKENIZER_GENERALIZATION_METRICS.csv", metrics_rows)
    write_csv_multi("TOKENIZER_CATEGORY_BREAKDOWN.csv", cat_rows)
    write_csv_multi("TOKENIZER_SCRIPT_GENERALIZATION.csv", script_rows)

    # 5. Throughput benchmark
    print("\nExecuting Throughput Benchmark (5 warmup runs, 5 timed runs across 3,000 records)...")
    texts = [r["text"] for r in records]
    total_words = sum(r["word_count"] for r in records)
    total_chars = sum(r["char_count"] for r in records)

    # Warmup
    for _ in range(3):
        for t in texts[:200]:
            tok_a.encode(t)
            tok_exp.encode(t)

    # Time encode A
    enc_times_a = []
    for _ in range(5):
        t0 = time.perf_counter()
        encs_a = [tok_a.encode(t) for t in texts]
        enc_times_a.append(time.perf_counter() - t0)
    mean_enc_time_a = statistics.mean(enc_times_a)

    # Time encode Exp
    enc_times_exp = []
    for _ in range(5):
        t0 = time.perf_counter()
        encs_exp = [tok_exp.encode(t) for t in texts]
        enc_times_exp.append(time.perf_counter() - t0)
    mean_enc_time_exp = statistics.mean(enc_times_exp)

    # Time decode A
    ids_list_a = [e.ids for e in encs_a]
    dec_times_a = []
    for _ in range(5):
        t0 = time.perf_counter()
        decs_a = [tok_a.decode(ids) for ids in ids_list_a]
        dec_times_a.append(time.perf_counter() - t0)
    mean_dec_time_a = statistics.mean(dec_times_a)

    # Time decode Exp
    ids_list_exp = [e.ids for e in encs_exp]
    dec_times_exp = []
    for _ in range(5):
        t0 = time.perf_counter()
        decs_exp = [tok_exp.decode(ids) for ids in ids_list_exp]
        dec_times_exp.append(time.perf_counter() - t0)
    mean_dec_time_exp = statistics.mean(dec_times_exp)

    perf_stats = {
        "mean_enc_time_a_sec": mean_enc_time_a,
        "mean_enc_time_exp_sec": mean_enc_time_exp,
        "enc_words_per_sec_a": total_words / mean_enc_time_a,
        "enc_words_per_sec_exp": total_words / mean_enc_time_exp,
        "enc_speedup_pct": ((mean_enc_time_a - mean_enc_time_exp) / mean_enc_time_a) * 100.0,
        "mean_dec_time_a_sec": mean_dec_time_a,
        "mean_dec_time_exp_sec": mean_dec_time_exp,
        "dec_words_per_sec_a": total_words / mean_dec_time_a,
        "dec_words_per_sec_exp": total_words / mean_dec_time_exp,
        "dec_speedup_pct": ((mean_dec_time_a - mean_dec_time_exp) / mean_dec_time_a) * 100.0,
    }

    print("\nBenchmark Speed Results:")
    print(f"  Candidate A Encode Throughput:     {perf_stats['enc_words_per_sec_a']:.1f} words/s")
    print(f"  Exp Candidate A Encode Throughput: {perf_stats['enc_words_per_sec_exp']:.1f} words/s ({perf_stats['enc_speedup_pct']:+.1f}%)")
    print(f"  Candidate A Decode Throughput:     {perf_stats['dec_words_per_sec_a']:.1f} words/s")
    print(f"  Exp Candidate A Decode Throughput: {perf_stats['dec_words_per_sec_exp']:.1f} words/s ({perf_stats['dec_speedup_pct']:+.1f}%)")

    # Save summary json
    summary_path = WORKSPACE_ROOT / "scratch" / "generalization_eval_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "metrics": metrics_rows,
            "categories": cat_rows,
            "scripts": script_rows,
            "perf": perf_stats
        }, f, indent=2)

    print("\nEvaluation complete! Summary saved to scratch/generalization_eval_summary.json")

if __name__ == "__main__":
    main()
