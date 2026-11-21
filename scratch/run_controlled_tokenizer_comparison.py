"""
scratch/run_controlled_tokenizer_comparison.py

Runs the complete, reproducible, controlled evaluation comparing:
- Original Candidate A (Hash: ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561)
- Experimental Candidate A (Hash: 3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce)
Across the 399 approved synthetic records and the 320/40/39 Train/Val/Test split.
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
from collections import Counter, defaultdict
from pathlib import Path
from tokenizers import Tokenizer

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")

sys.path.insert(0, str(PATCH_ROOT / "src"))
sys.path.insert(0, str(PATCH_ROOT / "scripts"))

ORIGINAL_CAND_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
ORIGINAL_CAND_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"
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

def compute_sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def percentile(vals, p):
    if not vals:
        return 0.0
    sorted_vals = sorted(vals)
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    d0 = sorted_vals[int(f)] * (c - k)
    d1 = sorted_vals[int(c)] * (k - f)
    return d0 + d1

def main():
    print("=" * 80)
    print("CONTROLLED TOKENIZER COMPARISON PIPELINE")
    print("=" * 80)

    # 1. Verify Hashes First
    cand_a_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    cand_b_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
    cand_exp_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"

    hash_a = compute_sha256(cand_a_path)
    hash_b = compute_sha256(cand_b_path)
    hash_exp = compute_sha256(cand_exp_path)

    assert hash_a == ORIGINAL_CAND_A_HASH, f"Cand A hash violation: {hash_a}"
    assert hash_b == ORIGINAL_CAND_B_HASH, f"Cand B hash violation: {hash_b}"
    assert hash_exp == EXPECTED_EXP_HASH, f"Cand Exp hash violation: {hash_exp}"
    print("[PASS] Tokenizer artifact cryptographic hashes strictly verified.")

    # 2. Load tokenizers
    tok_a = Tokenizer.from_file(str(cand_a_path))
    tok_exp = Tokenizer.from_file(str(cand_exp_path))

    # Verify structural tokens
    for expected_id, expected_tok in STRUCTURAL_TOKENS:
        act_a = tok_a.id_to_token(expected_id)
        act_exp = tok_exp.id_to_token(expected_id)
        assert act_a == expected_tok, f"Cand A structural mismatch at {expected_id}: {act_a} != {expected_tok}"
        assert act_exp == expected_tok, f"Cand Exp structural mismatch at {expected_id}: {act_exp} != {expected_tok}"
    print("[PASS] Structural tokens 0-11 verified in both tokenizers.")

    # 3. Load 399 approved records with multidimensional labels
    multidim_csv = PATCH_ROOT / "CANDIDATE_A_MULTIDIMENSIONAL_LANGUAGE_LABELS.csv"
    with open(multidim_csv, encoding="utf-8") as f:
        records = list(csv.DictReader(f))
    assert len(records) == 399

    # Load full texts from check_lang_labels
    import check_lang_labels
    doc_lookup = {f"SYN-CAND-A-{i + 1:04d}": d for i, d in enumerate(check_lang_labels.unique_docs)}
    for r in records:
        r["text"] = doc_lookup[r["doc_id"]]["text"]
        r["word_count"] = len(r["text"].split())
        r["char_count"] = len(r["text"])

    splits = Counter(r["split"] for r in records)
    print(f"Loaded {len(records)} records: Train={splits['TRAIN']}, Val={splits['VALIDATION']}, Test={splits['TEST']}")

    # 4. Evaluation Function
    def evaluate_subset(subset, name):
        words_total = sum(r["word_count"] for r in subset)
        chars_total = sum(r["char_count"] for r in subset)

        lens_a, lens_exp = [], []
        fert_word_a, fert_word_exp = [], []
        fert_char_a, fert_char_exp = [], []
        roundtrip_a, roundtrip_exp = 0, 0
        emitted_a, emitted_exp = set(), set()
        unk_a, unk_exp = 0, 0
        total_toks_a, total_toks_exp = 0, 0

        for r in subset:
            t = r["text"]
            w_cnt = r["word_count"]
            c_cnt = r["char_count"]

            # Encode A
            enc_a = tok_a.encode(t)
            ids_a = enc_a.ids
            lens_a.append(len(ids_a))
            fert_word_a.append(len(ids_a) / w_cnt if w_cnt > 0 else 0)
            fert_char_a.append(len(ids_a) / c_cnt if c_cnt > 0 else 0)
            emitted_a.update(ids_a)
            total_toks_a += len(ids_a)
            # check roundtrip A
            dec_a = tok_a.decode(ids_a)
            if unicodedata.normalize("NFC", dec_a) == unicodedata.normalize("NFC", t):
                roundtrip_a += 1

            # Encode Exp
            enc_exp = tok_exp.encode(t)
            ids_exp = enc_exp.ids
            lens_exp.append(len(ids_exp))
            fert_word_exp.append(len(ids_exp) / w_cnt if w_cnt > 0 else 0)
            fert_char_exp.append(len(ids_exp) / c_cnt if c_cnt > 0 else 0)
            emitted_exp.update(ids_exp)
            total_toks_exp += len(ids_exp)
            # check roundtrip Exp
            dec_exp = tok_exp.decode(ids_exp)
            if unicodedata.normalize("NFC", dec_exp) == unicodedata.normalize("NFC", t):
                roundtrip_exp += 1

        fert_word_avg_a = total_toks_a / words_total if words_total else 0
        fert_word_avg_exp = total_toks_exp / words_total if words_total else 0

        fert_char_avg_a = total_toks_a / chars_total if chars_total else 0
        fert_char_avg_exp = total_toks_exp / chars_total if chars_total else 0

        compression_gain = (total_toks_a - total_toks_exp) / total_toks_a * 100.0 if total_toks_a else 0.0

        return {
            "subset_name": name,
            "record_count": len(subset),
            "words_total": words_total,
            "chars_total": chars_total,
            # Candidate A
            "cand_a_total_tokens": total_toks_a,
            "cand_a_fertility_per_word": round(fert_word_avg_a, 4),
            "cand_a_fertility_per_char": round(fert_char_avg_a, 4),
            "cand_a_seq_len_median": round(statistics.median(lens_a), 2),
            "cand_a_seq_len_p90": round(percentile(lens_a, 90), 2),
            "cand_a_seq_len_p95": round(percentile(lens_a, 95), 2),
            "cand_a_seq_len_max": max(lens_a) if lens_a else 0,
            "cand_a_active_vocab_count": len(emitted_a),
            "cand_a_active_vocab_pct": round(len(emitted_a) / 32768 * 100, 2),
            "cand_a_roundtrip_accuracy": round(roundtrip_a / len(subset) * 100, 2) if subset else 0,
            # Experimental Candidate A
            "cand_exp_total_tokens": total_toks_exp,
            "cand_exp_fertility_per_word": round(fert_word_avg_exp, 4),
            "cand_exp_fertility_per_char": round(fert_char_avg_exp, 4),
            "cand_exp_seq_len_median": round(statistics.median(lens_exp), 2),
            "cand_exp_seq_len_p90": round(percentile(lens_exp, 90), 2),
            "cand_exp_seq_len_p95": round(percentile(lens_exp, 95), 2),
            "cand_exp_seq_len_max": max(lens_exp) if lens_exp else 0,
            "cand_exp_active_vocab_count": len(emitted_exp),
            "cand_exp_active_vocab_pct": round(len(emitted_exp) / 32768 * 100, 2),
            "cand_exp_roundtrip_accuracy": round(roundtrip_exp / len(subset) * 100, 2) if subset else 0,
            # Comparison
            "token_reduction_pct": round(compression_gain, 2),
        }

    # Run evaluations across splits
    subsets_to_eval = [
        ("ENTIRE_CORPUS", records),
        ("TRAIN_SPLIT", [r for r in records if r["split"] == "TRAIN"]),
        ("VAL_SPLIT", [r for r in records if r["split"] == "VALIDATION"]),
        ("TEST_SPLIT", [r for r in records if r["split"] == "TEST"]),
        # Operational Languages
        ("OPERATIONAL_TAMIL", [r for r in records if r["operational_language_label"] == "TAMIL"]),
        ("OPERATIONAL_ENGLISH", [r for r in records if r["operational_language_label"] == "ENGLISH"]),
        ("OPERATIONAL_TANGLISH", [r for r in records if r["operational_language_label"] == "TANGLISH"]),
        # Sub-types of Tanglish
        ("SUBTYPE_TAMIL_SCRIPT_TANGLISH", [r for r in records if r["operational_language_label"] == "TANGLISH" and r["script_form"] == "MIXED_SCRIPT" and any(0x0B80 <= ord(c) <= 0x0BFF for c in r["text"])]),
        ("SUBTYPE_ROMANIZED_TAMIL", [r for r in records if r["operational_language_label"] == "TANGLISH" and r["script_form"] == "LATIN_SCRIPT" and r["linguistic_matrix_language"] == "TAMIL"]),
        ("SUBTYPE_MIXED_SCRIPT_TANGLISH", [r for r in records if r["operational_language_label"] == "TANGLISH" and r["script_form"] == "MIXED_SCRIPT"]),
        ("SUBTYPE_ENGLISH_WITH_TAMIL_PARTICLES", [r for r in records if r["operational_language_label"] == "TANGLISH" and r["linguistic_matrix_language"] == "ENGLISH" and r["contains_tamil_discourse_markers"] == "YES"]),
    ]

    metrics_rows = []
    print("\nEvaluation Results Summary:")
    for name, s in subsets_to_eval:
        res = evaluate_subset(s, name)
        metrics_rows.append(res)
        print(f"  {name:36s} | N={res['record_count']:3d} | Orig A Fert={res['cand_a_fertility_per_word']:6.2f} | Exp A Fert={res['cand_exp_fertility_per_word']:6.2f} | Reduction: {res['token_reduction_pct']:5.1f}%")

    # 5. Measure Throughput (Warm-up + Repetitions)
    print("\nMeasuring Encode & Decode Throughput...")
    all_texts = [r["text"] for r in records]
    total_words = sum(r["word_count"] for r in records)
    total_chars = sum(r["char_count"] for r in records)

    # Warm-up (10 runs)
    for _ in range(10):
        for t in all_texts:
            tok_a.encode(t)
            tok_exp.encode(t)

    # Benchmark Encode A (5 repetitions)
    encode_times_a = []
    for _ in range(5):
        t0 = time.perf_counter()
        for t in all_texts:
            tok_a.encode(t)
        t1 = time.perf_counter()
        encode_times_a.append(t1 - t0)

    # Benchmark Encode Exp (5 repetitions)
    encode_times_exp = []
    for _ in range(5):
        t0 = time.perf_counter()
        for t in all_texts:
            tok_exp.encode(t)
        t1 = time.perf_counter()
        encode_times_exp.append(t1 - t0)

    # Pre-encode for Decode benchmark
    encoded_ids_a = [tok_a.encode(t).ids for t in all_texts]
    encoded_ids_exp = [tok_exp.encode(t).ids for t in all_texts]

    # Benchmark Decode A (5 repetitions)
    decode_times_a = []
    for _ in range(5):
        t0 = time.perf_counter()
        for ids in encoded_ids_a:
            tok_a.decode(ids)
        t1 = time.perf_counter()
        decode_times_a.append(t1 - t0)

    # Benchmark Decode Exp (5 repetitions)
    decode_times_exp = []
    for _ in range(5):
        t0 = time.perf_counter()
        for ids in encoded_ids_exp:
            tok_exp.decode(ids)
        t1 = time.perf_counter()
        decode_times_exp.append(t1 - t0)

    mean_enc_a = statistics.mean(encode_times_a)
    std_enc_a = statistics.stdev(encode_times_a)
    mean_enc_exp = statistics.mean(encode_times_exp)
    std_enc_exp = statistics.stdev(encode_times_exp)

    mean_dec_a = statistics.mean(decode_times_a)
    std_dec_a = statistics.stdev(decode_times_a)
    mean_dec_exp = statistics.mean(decode_times_exp)
    std_dec_exp = statistics.stdev(decode_times_exp)

    throughput_stats = {
        "hardware": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "backend": "tokenizers (Hugging Face Rust core)",
            "backend_version": "0.23.3",
        },
        "benchmark_conditions": {
            "records_evaluated": len(records),
            "words_total": total_words,
            "chars_total": total_chars,
            "warmup_procedure": "10 full corpus passes executed before measurement",
            "repetitions": 5,
            "timing_includes_preprocessing": False,
        },
        "candidate_a_timings": {
            "encode_time_mean_sec": round(mean_enc_a, 4),
            "encode_time_std_sec": round(std_enc_a, 4),
            "encode_words_per_sec": round(total_words / mean_enc_a, 1),
            "encode_chars_per_sec": round(total_chars / mean_enc_a, 1),
            "encode_ms_per_record": round(mean_enc_a / len(records) * 1000, 3),
            "decode_time_mean_sec": round(mean_dec_a, 4),
            "decode_time_std_sec": round(std_dec_a, 4),
            "decode_words_per_sec": round(total_words / mean_dec_a, 1),
            "decode_ms_per_record": round(mean_dec_a / len(records) * 1000, 3),
        },
        "candidate_exp_timings": {
            "encode_time_mean_sec": round(mean_enc_exp, 4),
            "encode_time_std_sec": round(std_enc_exp, 4),
            "encode_words_per_sec": round(total_words / mean_enc_exp, 1),
            "encode_chars_per_sec": round(total_chars / mean_enc_exp, 1),
            "encode_ms_per_record": round(mean_enc_exp / len(records) * 1000, 3),
            "decode_time_mean_sec": round(mean_dec_exp, 4),
            "decode_time_std_sec": round(std_dec_exp, 4),
            "decode_words_per_sec": round(total_words / mean_dec_exp, 1),
            "decode_ms_per_record": round(mean_dec_exp / len(records) * 1000, 3),
        }
    }

    print("\nThroughput Summary:")
    print(f"  Candidate A:     Encode: {throughput_stats['candidate_a_timings']['encode_words_per_sec']} words/s | Decode: {throughput_stats['candidate_a_timings']['decode_words_per_sec']} words/s")
    print(f"  Candidate Exp A: Encode: {throughput_stats['candidate_exp_timings']['encode_words_per_sec']} words/s | Decode: {throughput_stats['candidate_exp_timings']['decode_words_per_sec']} words/s")

    # 6. Tamil Adversarial & Unicode Test Suite
    print("\nRunning Adversarial & Unicode Test Suite...")
    adversarial_tests = [
        ("NFC_PULLI_CONJUNCT", "தமிழ்நாடு மென்பொருள் துறை", "Basic Tamil text with pulli viramas and consonants"),
        ("TAMIL_GRAPHEME_CONJUNCTS", "க்ஷ, ஸ்ரீ, ஶ்ரீ, க்‍க, க்‌க", "Grantha conjuncts (ksha, shri) and ligatures"),
        ("ZERO_WIDTH_JOINER", "க்\u200dக", "Tamil consonant + virama + ZWJ (U+200D)"),
        ("ZERO_WIDTH_NON_JOINER", "க்\u200cக", "Tamil consonant + virama + ZWNJ (U+200C)"),
        ("TAMIL_VOWEL_SIGNS", "கி, கீ, கு, கூ, கெ, கே, கை, கொ, கோ, கௌ", "Comprehensive vowel sign combinations"),
        ("TAMIL_NUMERALS_SYMBOLS", "௧௨௩௪௫௬௭௮௯௰ ௱ ௲ ௳ ௴ ௵", "Traditional Tamil digits and fraction symbols"),
        ("ROMANIZED_TAMIL_PHONETICS", "Innaiku nalla mazhai peyudhu pa, seekiram vaanga", "Colloquial Romanized Tamil"),
        ("NATURAL_CODE_SWITCHING", "Server restart aana udane API response latency check pannunga da", "Colloquial tech Tanglish"),
        ("MALFORMED_LONE_COMBINING", "\u0BBE\u0BF2\u0BCD", "Isolated combining vowel signs without base consonant"),
        ("STRUCTURAL_TOKENS_ISOLATION", "<|user|> What is IGRIS? <|assistant|> <think> Analyzing </think>", "Structural token delimiter handling"),
    ]

    unicode_results = []
    for test_name, text, desc in adversarial_tests:
        # Candidate A
        enc_a = tok_a.encode(text)
        dec_a = tok_a.decode(enc_a.ids)
        rt_a = (unicodedata.normalize("NFC", dec_a) == unicodedata.normalize("NFC", text))

        # Candidate Exp
        enc_exp = tok_exp.encode(text)
        dec_exp = tok_exp.decode(enc_exp.ids)
        rt_exp = (unicodedata.normalize("NFC", dec_exp) == unicodedata.normalize("NFC", text))

        unicode_results.append({
            "test_name": test_name,
            "description": desc,
            "raw_text_preview": repr(text),
            "cand_a_token_count": len(enc_a.ids),
            "cand_a_roundtrip_pass": "PASS" if rt_a else "FAIL",
            "cand_exp_token_count": len(enc_exp.ids),
            "cand_exp_roundtrip_pass": "PASS" if rt_exp else "FAIL",
            "efficiency_gain_pct": round((len(enc_a.ids) - len(enc_exp.ids)) / len(enc_a.ids) * 100, 1) if len(enc_a.ids) else 0.0,
        })
        print(f"  {test_name:30s} | A: {len(enc_a.ids):2d} toks ({'OK' if rt_a else 'FAIL'}) | Exp: {len(enc_exp.ids):2d} toks ({'OK' if rt_exp else 'FAIL'})")

    return metrics_rows, throughput_stats, unicode_results

if __name__ == "__main__":
    main()
