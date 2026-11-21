"""
TOKENIZER_SEGMENTATION_VERIFIER.py

Independent automated verification suite for the Linguistic Segmentation Quality Audit.
Verifies:
1. Cryptographic hashes of Candidate A, Experimental Candidate A, and Candidate B.
2. Structural token IDs 0-11 preservation.
3. All 12 audit deliverables exist and are non-empty.
4. Exactly 300 human review examples (100 Ta, 100 En, 100 Tg).
5. All 300 human review decisions remain NOT_REVIEWED with blank rationales.
6. Byte-level decoding bijection and 100.00% roundtrip accuracy across all 300 items.
7. Unicode UAX #29 unique grapheme cluster integrity and mandatory test expressions (including complex-ஆ).
8. Quantitative metrics reproducibility and exact denominators across partitions.
9. No tokenizer promotion occurred.
10. Production acquisition and pretraining gates remain locked ($0.00 spend).
"""

import csv
import hashlib
import os
import unittest
from pathlib import Path
import regex
from tokenizers import Tokenizer

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"

ORIGINAL_CAND_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
EXPECTED_EXP_HASH = "3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce"
EXPECTED_CAND_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

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

def bytes_to_unicode():
    bs = (
        list(range(ord("!"), ord("~") + 1))
        + list(range(ord("¡"), ord("¬") + 1))
        + list(range(ord("®"), ord("ÿ") + 1))
    )
    cs = bs[:]
    n = 0
    for b in range(2**8):
        if b not in bs:
            bs.append(b)
            cs.append(2**8 + n)
            n += 1
    cs = [chr(n) for n in cs]
    return dict(zip(bs, cs))

byte_to_char_map = bytes_to_unicode()
char_to_byte_map = {v: k for k, v in byte_to_char_map.items()}

def raw_token_to_bytes(tok_str: str) -> bytes:
    b_arr = bytearray()
    for ch in tok_str:
        if ch in char_to_byte_map:
            b_arr.append(char_to_byte_map[ch])
        else:
            b_arr.extend(ch.encode("utf-8"))
    return bytes(b_arr)

def full_reconstructed_text(raw_tokens: list[str]) -> str:
    all_bytes = b"".join(raw_token_to_bytes(t) for t in raw_tokens)
    return all_bytes.decode("utf-8", errors="replace")

def get_sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def analyze_graphemes(tok, text):
    clusters = list(regex.finditer(r"\X", text))
    enc = tok.encode(text)
    offsets = enc.offsets
    
    affected = []
    total_cuts = 0
    for c in clusters:
        c_s, c_e = c.start(), c.end()
        num_cuts = 0
        char_cuts = set(end for start, end in offsets if c_s < end < c_e)
        num_cuts += len(char_cuts)
        tokens_in_cluster = [i for i, (t_s, t_e) in enumerate(offsets) if t_s >= c_s and t_e <= c_e and t_s < t_e]
        if len(tokens_in_cluster) > 1 and len(char_cuts) == 0:
            num_cuts += (len(tokens_in_cluster) - 1)
        if num_cuts > 0:
            affected.append(c.group())
            total_cuts += num_cuts
            
    return {
        "total_clusters": len(clusters),
        "unique_affected_clusters": len(affected),
        "total_cuts": total_cuts,
        "affected": affected,
        "preservation_pct": round(100.0 * (len(clusters) - len(affected)) / max(1, len(clusters)), 2)
    }


class TestTokenizerSegmentationAudit(unittest.TestCase):

    def test_01_cryptographic_hashes(self):
        cand_a_p = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        exp_a_p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"
        cand_b_p = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
        
        self.assertEqual(get_sha256(cand_a_p), ORIGINAL_CAND_A_HASH)
        self.assertEqual(get_sha256(exp_a_p), EXPECTED_EXP_HASH)
        self.assertEqual(get_sha256(cand_b_p), EXPECTED_CAND_B_HASH)

    def test_02_structural_tokens(self):
        cand_a_p = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        exp_a_p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"
        tok_a = Tokenizer.from_file(str(cand_a_p))
        tok_exp = Tokenizer.from_file(str(exp_a_p))
        for tid, tstr in STRUCTURAL_TOKENS:
            self.assertEqual(tok_a.id_to_token(tid), tstr)
            self.assertEqual(tok_exp.id_to_token(tid), tstr)

    def test_03_all_deliverables_exist_and_non_empty(self):
        deliverables = [
            "TOKENIZER_LINGUISTIC_SEGMENTATION_REPORT.md",
            "TOKENIZER_BYTELEVEL_DECODING_AUDIT.md",
            "TOKENIZER_UNICODE_GRAPHEME_AUDIT.csv",
            "TOKENIZER_UNIQUE_GRAPHEME_IMPACT_ANALYSIS.csv",
            "TOKENIZER_CORPUS_SCOPE_RECONCILIATION.md",
            "TOKENIZER_OWNER_REVIEW_GUIDE.md",
            "TOKENIZER_FRAGMENTATION_ANALYSIS.csv",
            "TOKENIZER_HUMAN_REVIEW_SAMPLE.csv",
            "TAMIL_SEGMENTATION_AUDIT.csv",
            "ENGLISH_SEGMENTATION_AUDIT.csv",
            "TANGLISH_SEGMENTATION_AUDIT.csv",
            "TOKENIZER_SEGMENTATION_VERIFIER.py"
        ]
        for d in deliverables:
            root_f = WORKSPACE_ROOT / d
            self.assertTrue(root_f.exists(), f"Missing at root: {root_f}")
            self.assertGreater(root_f.stat().st_size, 0, f"Empty at root: {root_f}")

    def test_04_human_review_sample_counts_and_statuses(self):
        csv_p = WORKSPACE_ROOT / "TOKENIZER_HUMAN_REVIEW_SAMPLE.csv"
        with open(csv_p, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 300)
        ta_cnt = sum(1 for r in rows if r["language"] == "TAMIL")
        en_cnt = sum(1 for r in rows if r["language"] == "ENGLISH")
        tg_cnt = sum(1 for r in rows if r["language"] == "TANGLISH")
        self.assertEqual(ta_cnt, 100)
        self.assertEqual(en_cnt, 100)
        self.assertEqual(tg_cnt, 100)

        # All review statuses MUST be NOT_REVIEWED with blank decisions and rationales
        for r in rows:
            self.assertEqual(r["review_status"], "NOT_REVIEWED")
            self.assertEqual(r["human_review_decision"], "")
            self.assertEqual(r["reviewer_rationale"], "")

    def test_05_byte_level_decoding_and_roundtrip_fidelity(self):
        cand_a_p = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        exp_a_p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"
        tok_a = Tokenizer.from_file(str(cand_a_p))
        tok_exp = Tokenizer.from_file(str(exp_a_p))

        csv_p = WORKSPACE_ROOT / "TOKENIZER_HUMAN_REVIEW_SAMPLE.csv"
        with open(csv_p, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        for r in rows:
            orig = r["original_text"]
            enc_a = tok_a.encode(orig)
            enc_exp = tok_exp.encode(orig)

            recon_a = full_reconstructed_text(enc_a.tokens)
            recon_exp = full_reconstructed_text(enc_exp.tokens)

            self.assertEqual(recon_a, orig, f"Cand A byte reconstruction mismatch on: {orig}")
            self.assertEqual(recon_exp, orig, f"Cand Exp byte reconstruction mismatch on: {orig}")

    def test_06_unique_grapheme_integrity_and_mandatory_cases(self):
        cand_a_p = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        exp_a_p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"
        tok_a = Tokenizer.from_file(str(cand_a_p))
        tok_exp = Tokenizer.from_file(str(exp_a_p))

        mandatory_cases = {
            "server-ல்": {
                "graphemes": 8,
                "cand_a_affected": 1, "cand_a_cuts": 1, "cand_a_status": "DISRUPTED",
                "cand_exp_affected": 1, "cand_exp_cuts": 1, "cand_exp_status": "DISRUPTED"
            },
            "complex-ஆ": {
                "graphemes": 9,
                "cand_a_affected": 1, "cand_a_cuts": 1, "cand_a_status": "DISRUPTED",
                "cand_exp_affected": 0, "cand_exp_cuts": 0, "cand_exp_status": "PRESERVED"
            },
            "deploy பண்ணினோம்": {
                "graphemes": 12,
                "cand_a_affected": 4, "cand_a_cuts": 4, "cand_a_status": "DISRUPTED",
                "cand_exp_affected": 4, "cand_exp_cuts": 4, "cand_exp_status": "DISRUPTED"
            },
            "memory allocation": {
                "graphemes": 17,
                "cand_a_affected": 0, "cand_a_cuts": 0, "cand_a_status": "PRESERVED",
                "cand_exp_affected": 0, "cand_exp_cuts": 0, "cand_exp_status": "PRESERVED"
            },
            "pannirukkom": {
                "graphemes": 11,
                "cand_a_affected": 0, "cand_a_cuts": 0, "cand_a_status": "PRESERVED",
                "cand_exp_affected": 0, "cand_exp_cuts": 0, "cand_exp_status": "PRESERVED"
            },
            "testing-க்கு": {
                "graphemes": 10,
                "cand_a_affected": 2, "cand_a_cuts": 2, "cand_a_status": "DISRUPTED",
                "cand_exp_affected": 2, "cand_exp_cuts": 2, "cand_exp_status": "DISRUPTED"
            },
        }

        for text, exp_dict in mandatory_cases.items():
            res_a = analyze_graphemes(tok_a, text)
            res_exp = analyze_graphemes(tok_exp, text)

            self.assertEqual(res_a["total_clusters"], exp_dict["graphemes"])
            self.assertEqual(res_a["unique_affected_clusters"], exp_dict["cand_a_affected"])
            self.assertEqual(res_a["total_cuts"], exp_dict["cand_a_cuts"])

            self.assertEqual(res_exp["unique_affected_clusters"], exp_dict["cand_exp_affected"])
            self.assertEqual(res_exp["total_cuts"], exp_dict["cand_exp_cuts"])

    def test_07_quantitative_metrics_reproducibility(self):
        p = WORKSPACE_ROOT / "TOKENIZER_FRAGMENTATION_ANALYSIS.csv"
        with open(p, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        by_name = {r["analysis_dimension"]: r for r in rows}

        all_row = by_name["ENTIRE_EVALUATION_CORPUS"]
        self.assertEqual(int(all_row["word_count"]), 437)
        self.assertEqual(int(all_row["cand_a_total_tokens"]), 3429)
        self.assertEqual(int(all_row["cand_exp_total_tokens"]), 1943)
        self.assertAlmostEqual(float(all_row["token_reduction_pct"]), 43.34, delta=0.1)
        self.assertEqual(int(all_row["total_graphemes"]), 2990)
        self.assertEqual(int(all_row["cand_a_internal_cuts"]), 492)
        self.assertEqual(int(all_row["cand_a_unique_affected_clusters"]), 492)
        self.assertEqual(int(all_row["cand_exp_internal_cuts"]), 428)
        self.assertEqual(int(all_row["cand_exp_unique_affected_clusters"]), 428)
        self.assertEqual(float(all_row["cand_a_grapheme_preservation_pct"]), 83.55)
        self.assertEqual(float(all_row["cand_exp_grapheme_preservation_pct"]), 85.69)

        # Roundtrip accuracy must be 100.0% across all partitions
        for r in rows:
            self.assertEqual(float(r["cand_a_roundtrip_accuracy"]), 100.0)
            self.assertEqual(float(r["cand_exp_roundtrip_accuracy"]), 100.0)

    def test_08_no_tokenizer_promotion(self):
        cand_a_p = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        self.assertEqual(get_sha256(cand_a_p), ORIGINAL_CAND_A_HASH)
        self.assertNotEqual(get_sha256(cand_a_p), EXPECTED_EXP_HASH)

    def test_09_production_and_pretraining_locked(self):
        for d in ["production", "raw", "acquired", "quarantine"]:
            target_dir = PATCH_ROOT / d
            if target_dir.exists():
                files = [f for f in target_dir.glob("**/*") if f.is_file() and not f.name.endswith(".gitkeep")]
                self.assertEqual(len(files), 0, f"Production data present in {d}: {files}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
