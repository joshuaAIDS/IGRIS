"""
scratch/evaluate_generalization.py

Runs controlled evaluation of Candidate A vs Experimental Candidate A
across all 3,200 independent synthetic evaluation records.
Computes granular metrics across:
- Overall Corpus
- 3 Languages (Tamil, English, Tanglish)
- 3 Script Forms (Tamil Script, Latin Script, Mixed Script)
- 16 Semantic Categories
- Runtime Throughput
- Round-trip Unicode reconstruction
"""

import csv
import json
import statistics
import time
import unicodedata
from collections import Counter
from pathlib import Path
from tokenizers import Tokenizer

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"
cand_a_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
cand_exp_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"

tok_a = Tokenizer.from_file(str(cand_a_path))
tok_exp = Tokenizer.from_file(str(cand_exp_path))

import sys
sys.path.insert(0, str(WORKSPACE_ROOT / "scratch"))
import build_independent_synthetic_corpus as gen

records, orig_texts = gen.build_full_corpus()
print(f"Loaded {len(records)} evaluation records.")

def evaluate_subset(subset, subset_name):
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

        # Tokenizer A
        ids_a = tok_a.encode(t).ids
        lens_a.append(len(ids_a))
        emitted_a.update(ids_a)
        total_toks_a += len(ids_a)
        # Detokenize with special tokens preserved
        dec_a = tok_a.decode(ids_a, skip_special_tokens=False)
        if unicodedata.normalize("NFC", dec_a) == unicodedata.normalize("NFC", t):
            rt_a += 1

        # Tokenizer Exp
        ids_exp = tok_exp.encode(t).ids
        lens_exp.append(len(ids_exp))
        emitted_exp.update(ids_exp)
        total_toks_exp += len(ids_exp)
        dec_exp = tok_exp.decode(ids_exp, skip_special_tokens=False)
        if unicodedata.normalize("NFC", dec_exp) == unicodedata.normalize("NFC", t):
            rt_exp += 1

    fert_a = total_toks_a / words_total if words_total else 0.0
    fert_exp = total_toks_exp / words_total if words_total else 0.0
    tok_per_char_a = total_toks_a / chars_total if chars_total else 0.0
    tok_per_char_exp = total_toks_exp / chars_total if chars_total else 0.0

    p90_a = statistics.quantiles(lens_a, n=10)[8] if len(lens_a) >= 10 else max(lens_a)
    p95_a = statistics.quantiles(lens_a, n=20)[18] if len(lens_a) >= 20 else max(lens_a)
    p90_exp = statistics.quantiles(lens_exp, n=10)[8] if len(lens_exp) >= 10 else max(lens_exp)
    p95_exp = statistics.quantiles(lens_exp, n=20)[18] if len(lens_exp) >= 20 else max(lens_exp)

    tok_reduction_pct = ((total_toks_a - total_toks_exp) / total_toks_a) * 100.0 if total_toks_a else 0.0

    return {
        "subset_name": subset_name,
        "record_count": len(subset),
        "words_total": words_total,
        "chars_total": chars_total,
        "tokens_a": total_toks_a,
        "fertility_a": round(fert_a, 4),
        "tok_per_char_a": round(tok_per_char_a, 4),
        "seq_len_median_a": statistics.median(lens_a),
        "seq_len_p90_a": p90_a,
        "seq_len_p95_a": p95_a,
        "seq_len_max_a": max(lens_a),
        "tokens_exp": total_toks_exp,
        "fertility_exp": round(fert_exp, 4),
        "tok_per_char_exp": round(tok_per_char_exp, 4),
        "seq_len_median_exp": statistics.median(lens_exp),
        "seq_len_p90_exp": p90_exp,
        "seq_len_p95_exp": p95_exp,
        "seq_len_max_exp": max(lens_exp),
        "token_reduction_pct": round(tok_reduction_pct, 2),
        "active_vocab_a": len(emitted_a),
        "active_vocab_exp": len(emitted_exp),
        "roundtrip_acc_a": round((rt_a / len(subset)) * 100.0, 2),
        "roundtrip_acc_exp": round((rt_exp / len(subset)) * 100.0, 2)
    }

if __name__ == "__main__":
    print("\n--- 1. OVERALL CORPUS & LANGUAGES ---")
    overall = evaluate_subset(records, "ENTIRE_INDEPENDENT_CORPUS")
    print(f"Overall: N={overall['record_count']} A_fert={overall['fertility_a']} Exp_fert={overall['fertility_exp']} Gain={overall['token_reduction_pct']}% ActiveA={overall['active_vocab_a']} ActiveExp={overall['active_vocab_exp']}")

    lang_results = {}
    for lang in ["TAMIL", "ENGLISH", "TANGLISH"]:
        sub = [r for r in records if r["operational_language"] == lang]
        res = evaluate_subset(sub, f"LANG_{lang}")
        lang_results[lang] = res
        print(f"Lang {lang:10s}: N={res['record_count']:4d} A_fert={res['fertility_a']:6.2f} Exp_fert={res['fertility_exp']:6.2f} Gain={res['token_reduction_pct']:5.2f}%")

    print("\n--- 2. SCRIPT FORMS ---")
    script_results = {}
    for s in ["TAMIL_SCRIPT", "LATIN_SCRIPT", "MIXED_SCRIPT"]:
        sub = [r for r in records if r["script_form"] == s]
        res = evaluate_subset(sub, f"SCRIPT_{s}")
        script_results[s] = res
        print(f"Script {s:15s}: N={res['record_count']:4d} A_fert={res['fertility_a']:6.2f} Exp_fert={res['fertility_exp']:6.2f} Gain={res['token_reduction_pct']:5.2f}%")

    print("\n--- 3. 16 SEMANTIC CATEGORIES ---")
    cat_names = [
        "TAMIL_CONVERSATIONAL", "TAMIL_FORMAL", "TAMIL_EDUCATIONAL", "TAMIL_TECHNICAL", "TAMIL_LONGFORM",
        "ENGLISH_CONVERSATIONAL", "ENGLISH_TECHNICAL_DOCS", "ENGLISH_PROGRAMMING", "ENGLISH_EDUCATIONAL", "ENGLISH_LONGFORM",
        "TANGLISH_ROMANIZED", "TANGLISH_TAMIL_SCRIPT_TECH", "TANGLISH_ENGLISH_TAMIL_PARTICLES", "TANGLISH_INTRA_SENTENTIAL", "TANGLISH_INFORMAL", "TANGLISH_FORMAL_TECH"
    ]
    category_results = {}
    for cat in cat_names:
        sub = [r for r in records if r["category"] == cat]
        res = evaluate_subset(sub, cat)
        category_results[cat] = res
        print(f"Cat {cat:35s}: N={res['record_count']:3d} A_fert={res['fertility_a']:6.2f} Exp_fert={res['fertility_exp']:6.2f} Gain={res['token_reduction_pct']:5.2f}%")

    print("\n--- 4. THROUGHPUT BENCHMARK ---")
    texts = [r["text"] for r in records]
    total_words = sum(r["word_count"] for r in records)

    # Warmup
    for _ in range(10):
        for t in texts[:100]:
            tok_a.encode(t)
            tok_exp.encode(t)

    # Encode benchmark (5 passes over all 3200 records)
    t0 = time.perf_counter()
    for _ in range(5):
        for t in texts:
            tok_a.encode(t)
    t1 = time.perf_counter()
    time_a = (t1 - t0) / 5
    enc_speed_a = total_words / time_a

    t0 = time.perf_counter()
    for _ in range(5):
        for t in texts:
            tok_exp.encode(t)
    t1 = time.perf_counter()
    time_exp = (t1 - t0) / 5
    enc_speed_exp = total_words / time_exp

    # Decode benchmark (pre-encoded IDs)
    ids_a_all = [tok_a.encode(t).ids for t in texts]
    ids_exp_all = [tok_exp.encode(t).ids for t in texts]

    t0 = time.perf_counter()
    for _ in range(5):
        for ids in ids_a_all:
            tok_a.decode(ids, skip_special_tokens=False)
    t1 = time.perf_counter()
    dec_time_a = (t1 - t0) / 5
    dec_speed_a = total_words / dec_time_a

    t0 = time.perf_counter()
    for _ in range(5):
        for ids in ids_exp_all:
            tok_exp.decode(ids, skip_special_tokens=False)
    t1 = time.perf_counter()
    dec_time_exp = (t1 - t0) / 5
    dec_speed_exp = total_words / dec_time_exp

    print(f"Encode Speed Cand A: {enc_speed_a:,.1f} words/s ({time_a*1000/len(texts):.3f} ms/doc)")
    print(f"Encode Speed Exp A:  {enc_speed_exp:,.1f} words/s ({time_exp*1000/len(texts):.3f} ms/doc)")
    print(f"Decode Speed Cand A: {dec_speed_a:,.1f} words/s ({dec_time_a*1000/len(texts):.3f} ms/doc)")
    print(f"Decode Speed Exp A:  {dec_speed_exp:,.1f} words/s ({dec_time_exp*1000/len(texts):.3f} ms/doc)")
