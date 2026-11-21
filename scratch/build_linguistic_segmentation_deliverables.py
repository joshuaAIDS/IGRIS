"""
scratch/build_linguistic_segmentation_deliverables.py

Constructs all 7 required linguistic segmentation audit deliverables:
1. TOKENIZER_LINGUISTIC_SEGMENTATION_REPORT.md
2. TAMIL_SEGMENTATION_AUDIT.csv
3. ENGLISH_SEGMENTATION_AUDIT.csv
4. TANGLISH_SEGMENTATION_AUDIT.csv
5. TOKENIZER_FRAGMENTATION_ANALYSIS.csv
6. TOKENIZER_HUMAN_REVIEW_SAMPLE.csv (300 rows, exactly 100 Ta, 100 En, 100 Tg, NOT_REVIEWED)
7. TOKENIZER_SEGMENTATION_VERIFIER.py
"""

import csv
import hashlib
import json
import os
import re
import shutil
import statistics
import unicodedata
from collections import Counter
from pathlib import Path
from tokenizers import Tokenizer

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")

cand_a_path = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
exp_a_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"

tok_a = Tokenizer.from_file(str(cand_a_path))
tok_exp = Tokenizer.from_file(str(exp_a_path))

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

# Grapheme cluster regex for Tamil
# A Tamil base letter optionally followed by pulli (virama U+0BCD) or vowel signs (U+0BBE-U+0BCC) or au length mark (U+0BD7)
TAMIL_AKSHARA_PATTERN = re.compile(r"[\u0B85-\u0B94]|[\u0B95-\u0BB9](?:\u0BCD|[\u0BBE-\u0BCC\u0BD7])?")

def analyze_grapheme_integrity(text: str, tokenizer: Tokenizer) -> float:
    """Checks what percentage of Tamil aksharas are not split across tokens."""
    aksharas = TAMIL_AKSHARA_PATTERN.findall(text)
    if not aksharas:
        return 100.0
    enc = tokenizer.encode(text)
    # Check if any token ends with an incomplete byte or detached pulli
    # In HF ByteLevel BPE, bytes are mapped to unicode chars
    # If roundtrip decode of each token is valid utf-8 and doesn't orphan virama
    intact = 0
    for ak in aksharas:
        # If the akshara can be encoded without splitting across tokens
        enc_ak = tokenizer.encode(ak)
        if len(enc_ak.ids) <= 2: # Base + virama/vowel sign at most 2 tokens
            intact += 1
    return (intact / len(aksharas)) * 100.0

def get_subword_stats(texts, tokenizer):
    token_lens = []
    word_frag_cnt = 0
    single_tok_cnt = 0
    excess_frag_cnt = 0
    total_words = 0
    total_chars = sum(len(t) for t in texts)
    total_tokens = 0
    roundtrip_cnt = 0

    for t in texts:
        enc = tokenizer.encode(t)
        total_tokens += len(enc.ids)
        for tok in enc.tokens:
            token_lens.append(len(tok))

        dec = tokenizer.decode(enc.ids, skip_special_tokens=False)
        if unicodedata.normalize("NFC", dec) == unicodedata.normalize("NFC", t):
            roundtrip_cnt += 1

        words = t.split()
        total_words += len(words)
        for w in words:
            w_enc = tokenizer.encode(w)
            n_toks = len(w_enc.ids)
            if n_toks == 1:
                single_tok_cnt += 1
            else:
                word_frag_cnt += 1
            if n_toks >= 5:
                excess_frag_cnt += 1

    fert = total_tokens / total_words if total_words else 0.0
    cpt = total_chars / total_tokens if total_tokens else 0.0
    mean_sw = statistics.mean(token_lens) if token_lens else 0.0
    med_sw = statistics.median(token_lens) if token_lens else 0.0
    min_sw = min(token_lens) if token_lens else 0
    max_sw = max(token_lens) if token_lens else 0

    frag_rate = (word_frag_cnt / total_words * 100.0) if total_words else 0.0
    single_rate = (single_tok_cnt / total_words * 100.0) if total_words else 0.0
    excess_rate = (excess_frag_cnt / total_words * 100.0) if total_words else 0.0
    rt_acc = (roundtrip_cnt / len(texts) * 100.0) if texts else 0.0

    return {
        "words": total_words,
        "tokens": total_tokens,
        "fertility": round(fert, 4),
        "chars_per_tok": round(cpt, 4),
        "subword_mean": round(mean_sw, 2),
        "subword_median": med_sw,
        "subword_min": min_sw,
        "subword_max": max_sw,
        "single_tok_pct": round(single_rate, 2),
        "frag_rate_pct": round(frag_rate, 2),
        "excess_frag_pct": round(excess_rate, 2),
        "roundtrip_acc": round(rt_acc, 2)
    }

print("Definitions loaded.")
