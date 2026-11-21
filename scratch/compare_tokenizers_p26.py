import hashlib
import json
import time
import tracemalloc
from pathlib import Path
from collections import defaultdict
import numpy as np

PATCH_DIR = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")

tok_a_path = PATCH_DIR / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
tok_b_path = PATCH_DIR / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"

h_a = hashlib.sha256(open(tok_a_path, "rb").read()).hexdigest()
h_b = hashlib.sha256(open(tok_b_path, "rb").read()).hexdigest()

print("Candidate A Hash:", h_a)
print("Candidate B Hash:", h_b)

from tokenizers import Tokenizer
import sentencepiece as spm

tok_a = Tokenizer.from_file(str(tok_a_path))
sp_b = spm.SentencePieceProcessor()
sp_b.load(str(tok_b_path))

with open(PATCH_DIR / "PHASE26_DATASET_SPLITS.json", "r", encoding="utf-8") as f:
    pkg = json.load(f)

# Collect all valid texts across dev, val, test
all_records = []
for split in ["dev", "val", "test"]:
    for r in pkg["splits"][split]:
        if r["expected_quality_pass"] and not r["expected_duplicate"]:
            all_records.append(r)

print(f"Total clean evaluation records for tokenizer comparison: {len(all_records)}")

# Benchmark Candidate A
tracemalloc.start()
t0_a = time.perf_counter()
tok_a_results = []
a_tokens_total = 0
a_words_total = 0
a_unk_total = 0
a_roundtrip_ok = 0
a_seq_lens = []

unk_id_a = tok_a.token_to_id("[UNK]")
if unk_id_a is None:
    unk_id_a = tok_a.token_to_id("<unk>")

for r in all_records:
    text = r["text"]
    w_cnt = len(text.split())
    enc = tok_a.encode(text)
    ids = enc.ids
    a_tokens_total += len(ids)
    a_words_total += w_cnt
    a_seq_lens.append(len(ids))
    u_cnt = sum(1 for tid in ids if tid == unk_id_a) if unk_id_a is not None else 0
    a_unk_total += u_cnt
    dec = tok_a.decode(ids)
    if dec.strip() == text.strip():
        a_roundtrip_ok += 1

t1_a = time.perf_counter()
current_a, peak_a = tracemalloc.get_traced_memory()
tracemalloc.stop()
time_a = t1_a - t0_a
speed_a = a_tokens_total / time_a if time_a > 0 else 0

# Benchmark Candidate B
tracemalloc.start()
t0_b = time.perf_counter()
b_tokens_total = 0
b_words_total = 0
b_unk_total = 0
b_roundtrip_ok = 0
b_seq_lens = []

unk_id_b = sp_b.unk_id()

for r in all_records:
    text = r["text"]
    w_cnt = len(text.split())
    ids = sp_b.encode_as_ids(text)
    b_tokens_total += len(ids)
    b_words_total += w_cnt
    b_seq_lens.append(len(ids))
    u_cnt = sum(1 for tid in ids if tid == unk_id_b)
    b_unk_total += u_cnt
    dec = sp_b.decode_ids(ids)
    if dec.strip() == text.strip():
        b_roundtrip_ok += 1

t1_b = time.perf_counter()
current_b, peak_b = tracemalloc.get_traced_memory()
tracemalloc.stop()
time_b = t1_b - t0_b
speed_b = b_tokens_total / time_b if time_b > 0 else 0

print("\n--- Candidate A (ByteLevel BPE) ---")
print(f"Total tokens: {a_tokens_total}")
print(f"Overall fertility: {a_tokens_total / a_words_total:.4f}")
print(f"UNK rate: {a_unk_total / a_tokens_total:.6f} ({a_unk_total} UNKs)")
print(f"Roundtrip lossless: {a_roundtrip_ok}/{len(all_records)} ({a_roundtrip_ok/len(all_records):.2%})")
print(f"Encoding speed: {speed_a:.1f} tokens/sec")
print(f"Peak memory: {peak_a / 1024:.2f} KB")
print(f"Seq lens: min={min(a_seq_lens)}, max={max(a_seq_lens)}, mean={np.mean(a_seq_lens):.1f}, median={np.median(a_seq_lens)}, p95={np.percentile(a_seq_lens, 95):.1f}")

print("\n--- Candidate B (SentencePiece) ---")
print(f"Total tokens: {b_tokens_total}")
print(f"Overall fertility: {b_tokens_total / b_words_total:.4f}")
print(f"UNK rate: {b_unk_total / b_tokens_total:.6f} ({b_unk_total} UNKs)")
print(f"Roundtrip lossless: {b_roundtrip_ok}/{len(all_records)} ({b_roundtrip_ok/len(all_records):.2%})")
print(f"Encoding speed: {speed_b:.1f} tokens/sec")
print(f"Peak memory: {peak_b / 1024:.2f} KB")
print(f"Seq lens: min={min(b_seq_lens)}, max={max(b_seq_lens)}, mean={np.mean(b_seq_lens):.1f}, median={np.median(b_seq_lens)}, p95={np.percentile(b_seq_lens, 95):.1f}")
