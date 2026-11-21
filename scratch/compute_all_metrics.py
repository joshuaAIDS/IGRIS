"""
scratch/compute_all_metrics.py

Computes all granular metrics for:
- TOKENIZER_COMPARISON_METRICS.csv
- TOKENIZER_LANGUAGE_BREAKDOWN.csv
- TOKENIZER_SCRIPT_BREAKDOWN.csv
"""

import csv
import json
import statistics
import unicodedata
from collections import Counter
from pathlib import Path
from tokenizers import Tokenizer
import run_controlled_tokenizer_comparison as comp

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
cand_a_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
cand_exp_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"

tok_a = Tokenizer.from_file(str(cand_a_path))
tok_exp = Tokenizer.from_file(str(cand_exp_path))

# Load multidimensional records
multidim_csv = PATCH_ROOT / "CANDIDATE_A_MULTIDIMENSIONAL_LANGUAGE_LABELS.csv"
with open(multidim_csv, encoding="utf-8") as f:
    records = list(csv.DictReader(f))

import check_lang_labels
doc_lookup = {f"SYN-CAND-A-{i + 1:04d}": d for i, d in enumerate(check_lang_labels.unique_docs)}
for r in records:
    r["text"] = doc_lookup[r["doc_id"]]["text"]
    r["word_count"] = len(r["text"].split())
    r["char_count"] = len(r["text"])

def evaluate(subset, name):
    words_total = sum(r["word_count"] for r in subset)
    chars_total = sum(r["char_count"] for r in subset)
    lens_a, lens_exp = [], []
    emitted_a, emitted_exp = set(), set()
    total_toks_a, total_toks_exp = 0, 0
    rt_a, rt_exp = 0, 0

    for r in subset:
        t = r["text"]
        c_cnt = r["char_count"]
        w_cnt = r["word_count"]

        ids_a = tok_a.encode(t).ids
        lens_a.append(len(ids_a))
        emitted_a.update(ids_a)
        total_toks_a += len(ids_a)
        if unicodedata.normalize("NFC", tok_a.decode(ids_a, skip_special_tokens=False)) == unicodedata.normalize("NFC", t):
            rt_a += 1

        ids_exp = tok_exp.encode(t).ids
        lens_exp.append(len(ids_exp))
        emitted_exp.update(ids_exp)
        total_toks_exp += len(ids_exp)
        if unicodedata.normalize("NFC", tok_exp.decode(ids_exp, skip_special_tokens=False)) == unicodedata.normalize("NFC", t):
            rt_exp += 1

    fert_word_a = total_toks_a / words_total if words_total else 0
    fert_word_exp = total_toks_exp / words_total if words_total else 0

    fert_char_a = total_toks_a / chars_total if chars_total else 0
    fert_char_exp = total_toks_exp / chars_total if chars_total else 0

    red_pct = (total_toks_a - total_toks_exp) / total_toks_a * 100.0 if total_toks_a else 0.0

    return {
        "subset_name": name,
        "record_count": len(subset),
        "words_total": words_total,
        "chars_total": chars_total,
        "cand_a_total_tokens": total_toks_a,
        "cand_a_fertility_per_word": round(fert_word_a, 4),
        "cand_a_fertility_per_char": round(fert_char_a, 4),
        "cand_a_seq_len_median": round(statistics.median(lens_a), 2) if lens_a else 0,
        "cand_a_seq_len_p90": round(comp.percentile(lens_a, 90), 2) if lens_a else 0,
        "cand_a_seq_len_p95": round(comp.percentile(lens_a, 95), 2) if lens_a else 0,
        "cand_a_seq_len_max": max(lens_a) if lens_a else 0,
        "cand_a_active_vocab_count": len(emitted_a),
        "cand_a_active_vocab_pct": round(len(emitted_a) / 32768 * 100, 2),
        "cand_a_roundtrip_accuracy": round(rt_a / len(subset) * 100, 2) if subset else 0,
        "cand_exp_total_tokens": total_toks_exp,
        "cand_exp_fertility_per_word": round(fert_word_exp, 4),
        "cand_exp_fertility_per_char": round(fert_char_exp, 4),
        "cand_exp_seq_len_median": round(statistics.median(lens_exp), 2) if lens_exp else 0,
        "cand_exp_seq_len_p90": round(comp.percentile(lens_exp, 90), 2) if lens_exp else 0,
        "cand_exp_seq_len_p95": round(comp.percentile(lens_exp, 95), 2) if lens_exp else 0,
        "cand_exp_seq_len_max": max(lens_exp) if lens_exp else 0,
        "cand_exp_active_vocab_count": len(emitted_exp),
        "cand_exp_active_vocab_pct": round(len(emitted_exp) / 32768 * 100, 2),
        "cand_exp_roundtrip_accuracy": round(rt_exp / len(subset) * 100, 2) if subset else 0,
        "token_reduction_pct": round(red_pct, 2),
    }

# 1. Main comparison metrics: Splits
main_splits = [
    ("ENTIRE_CORPUS", records),
    ("TRAIN_SPLIT", [r for r in records if r["split"] == "TRAIN"]),
    ("VAL_SPLIT", [r for r in records if r["split"] == "VALIDATION"]),
    ("TEST_SPLIT", [r for r in records if r["split"] == "TEST"]),
]

# 2. Language breakdown
lang_subsets = [
    ("OPERATIONAL_TAMIL", [r for r in records if r["operational_language_label"] == "TAMIL"]),
    ("OPERATIONAL_ENGLISH", [r for r in records if r["operational_language_label"] == "ENGLISH"]),
    ("OPERATIONAL_TANGLISH", [r for r in records if r["operational_language_label"] == "TANGLISH"]),
    ("MATRIX_TAMIL", [r for r in records if r["linguistic_matrix_language"] == "TAMIL"]),
    ("MATRIX_ENGLISH", [r for r in records if r["linguistic_matrix_language"] == "ENGLISH"]),
    ("MATRIX_TANGLISH", [r for r in records if r["linguistic_matrix_language"] == "TANGLISH"]),
    ("SUBTYPE_TAMIL_SCRIPT_TANGLISH", [r for r in records if r["operational_language_label"] == "TANGLISH" and r["script_form"] == "MIXED_SCRIPT" and any(0x0B80 <= ord(c) <= 0x0BFF for c in r["text"])]),
    ("SUBTYPE_ROMANIZED_TAMIL", [r for r in records if r["operational_language_label"] == "TANGLISH" and r["script_form"] == "LATIN_SCRIPT" and r["romanized_tamil_present"] == "YES"]),
    ("SUBTYPE_MIXED_SCRIPT_TANGLISH", [r for r in records if r["operational_language_label"] == "TANGLISH" and r["script_form"] == "MIXED_SCRIPT"]),
    ("SUBTYPE_ENGLISH_WITH_TAMIL_PARTICLES", [r for r in records if r["operational_language_label"] == "TANGLISH" and r["linguistic_matrix_language"] == "ENGLISH" and r["contains_tamil_discourse_markers"] == "YES"]),
]

# 3. Script breakdown
script_subsets = [
    ("TAMIL_SCRIPT", [r for r in records if r["script_form"] == "TAMIL_SCRIPT"]),
    ("LATIN_SCRIPT", [r for r in records if r["script_form"] == "LATIN_SCRIPT"]),
    ("MIXED_SCRIPT", [r for r in records if r["script_form"] == "MIXED_SCRIPT"]),
]

print("Computing Splits...")
res_splits = [evaluate(s, n) for n, s in main_splits]
print("Computing Languages...")
res_langs = [evaluate(s, n) for n, s in lang_subsets]
print("Computing Scripts...")
res_scripts = [evaluate(s, n) for n, s in script_subsets]

print("Done. Sample:")
for r in res_splits:
    print(r["subset_name"], "N=", r["record_count"], "A=", r["cand_a_fertility_per_word"], "Exp=", r["cand_exp_fertility_per_word"], "Gain=", r["token_reduction_pct"])
