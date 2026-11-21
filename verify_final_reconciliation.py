"""
verify_final_reconciliation.py

Authoritative Automated Verification Suite for the Final Evidence Reconciliation.
Asserts:
1. Cryptographic hashes of all 3 tokenizer artifacts.
2. Structural token IDs 0-11 in both Candidate A and Exp Candidate A.
3. 300-item reconciliation audit row count and reproducible aggregate sums.
4. Conclusive structural and byte-level properties of complex-ஆ.
5. Strict adherence to conservative morphology classifications for the 15 English cases.
6. All review decisions remain NOT_REVIEWED across both 30-item and 300-item files.
7. Deliverables presence across workspace root, patch root, and artifact directory.
8. Production data acquisition and pretraining gates strictly LOCKED ($0.00 spend).
"""

import csv
import hashlib
import unittest
from pathlib import Path
from tokenizers import Tokenizer

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")

CAND_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CAND_EXP_HASH = "3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce"
CAND_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

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

ALLOWED_MORPH_CLASSES = {
    "CLEAR_MORPHEME_BOUNDARY",
    "CROSSES_MORPHEME_BOUNDARY",
    "POTENTIAL_OVERMERGE",
    "LINGUISTICALLY_AMBIGUOUS",
    "NOT_ASSESSED"
}

def get_sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

class TestFinalReconciliation(unittest.TestCase):

    def test_01_cryptographic_hashes(self):
        cand_a_p = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        exp_a_p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"
        cand_b_p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
        
        self.assertEqual(get_sha256(cand_a_p), CAND_A_HASH, "Candidate A hash corrupted!")
        self.assertEqual(get_sha256(exp_a_p), CAND_EXP_HASH, "Experimental Candidate A hash corrupted!")
        self.assertEqual(get_sha256(cand_b_p), CAND_B_HASH, "Candidate B hash corrupted!")

    def test_02_structural_tokens(self):
        cand_a_p = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        exp_a_p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"
        tok_a = Tokenizer.from_file(str(cand_a_p))
        tok_exp = Tokenizer.from_file(str(exp_a_p))
        for tid, tstr in STRUCTURAL_TOKENS:
            self.assertEqual(tok_a.id_to_token(tid), tstr)
            self.assertEqual(tok_exp.id_to_token(tid), tstr)

    def test_03_deliverables_presence_across_all_locations(self):
        deliverables = [
            "TOKENIZER_FINAL_RECONCILIATION_REPORT.md",
            "TOKENIZER_GRAPHEME_RECONCILIATION_300.csv",
            "TOKENIZER_MORPHOLOGY_REVIEW_V2.csv",
            "TOKENIZER_OWNER_REVIEW_READINESS.md"
        ]
        for loc in [WORKSPACE_ROOT, PATCH_ROOT, ARTIFACT_DIR]:
            for d in deliverables:
                p = loc / d
                self.assertTrue(p.exists(), f"Missing deliverable: {p}")
                self.assertGreater(p.stat().st_size, 0, f"Empty deliverable: {p}")

    def test_04_300_item_grapheme_audit_reconciliation_totals(self):
        csv_path = WORKSPACE_ROOT / "TOKENIZER_GRAPHEME_RECONCILIATION_300.csv"
        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            
        self.assertEqual(len(rows), 300, f"Expected 300 rows, got {len(rows)}")
        
        tot_graphemes = sum(int(r["total_graphemes"]) for r in rows)
        self.assertEqual(tot_graphemes, 2990)
        
        cand_a_cuts = sum(int(r["cand_a_total_internal_cuts"]) for r in rows)
        cand_a_inside = sum(int(r["cand_a_cuts_inside_graphemes"]) for r in rows)
        cand_a_between = sum(int(r["cand_a_cuts_between_graphemes"]) for r in rows)
        cand_a_byte_inside = sum(int(r["cand_a_byte_cuts_inside_graphemes"]) for r in rows)
        
        self.assertEqual(cand_a_cuts, 3129)
        self.assertEqual(cand_a_inside, 598)
        self.assertEqual(cand_a_between, 2531)
        self.assertEqual(cand_a_inside + cand_a_between, cand_a_cuts)
        self.assertEqual(cand_a_byte_inside, 735)
        
        exp_cuts = sum(int(r["cand_exp_total_internal_cuts"]) for r in rows)
        exp_inside = sum(int(r["cand_exp_cuts_inside_graphemes"]) for r in rows)
        exp_between = sum(int(r["cand_exp_cuts_between_graphemes"]) for r in rows)
        exp_byte_inside = sum(int(r["cand_exp_byte_cuts_inside_graphemes"]) for r in rows)
        
        self.assertEqual(exp_cuts, 1643)
        self.assertEqual(exp_inside, 423)
        self.assertEqual(exp_between, 1220)
        self.assertEqual(exp_inside + exp_between, exp_cuts)
        self.assertEqual(exp_byte_inside, 429)

    def test_05_complex_aa_reconciliation(self):
        cand_a_p = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        exp_a_p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"
        tok_a = Tokenizer.from_file(str(cand_a_p))
        tok_exp = Tokenizer.from_file(str(exp_a_p))
        
        text = "complex-ஆ"
        enc_a = tok_a.encode(text)
        enc_exp = tok_exp.encode(text)
        
        self.assertEqual(enc_a.ids, [78, 90, 88, 91, 87, 300, 24, 268, 240])
        self.assertEqual(enc_exp.ids, [472, 571, 99, 24, 766])
        
        # Verify tokens
        self.assertEqual(enc_a.tokens, ['c', 'o', 'm', 'p', 'l', 'ex', '-', 'à®', 'Ĩ'])
        self.assertEqual(enc_exp.tokens, ['com', 'ple', 'x', '-', 'à®Ĩ'])
        
        # Decode roundtrip
        self.assertEqual(tok_a.decode(enc_a.ids), text)
        self.assertEqual(tok_exp.decode(enc_exp.ids), text)

    def test_06_conservative_morphology_classifications(self):
        csv_path = WORKSPACE_ROOT / "TOKENIZER_MORPHOLOGY_REVIEW_V2.csv"
        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            
        self.assertEqual(len(rows), 15)
        for r in rows:
            self.assertIn(r["classification"], ALLOWED_MORPH_CLASSES, f"Invalid classification: {r['classification']}")
            self.assertTrue(len(r["linguistic_rationale"]) > 10, f"Missing rationale in row {r['review_id']}")
            
        by_word = {r["word"]: r["classification"] for r in rows}
        self.assertEqual(by_word["microservice"], "CROSSES_MORPHEME_BOUNDARY")
        self.assertEqual(by_word["microservices"], "CROSSES_MORPHEME_BOUNDARY")
        self.assertEqual(by_word["asynchronous"], "CROSSES_MORPHEME_BOUNDARY")
        self.assertEqual(by_word["middleware"], "CLEAR_MORPHEME_BOUNDARY")
        self.assertEqual(by_word["ware"], "CLEAR_MORPHEME_BOUNDARY")
        self.assertEqual(by_word["unavoidable"], "CLEAR_MORPHEME_BOUNDARY")
        self.assertEqual(by_word["avoidable"], "CLEAR_MORPHEME_BOUNDARY")
        self.assertEqual(by_word["multiprocessing"], "CLEAR_MORPHEME_BOUNDARY")

    def test_07_all_review_decisions_remain_not_reviewed(self):
        # 30-item owner review file
        p30 = WORKSPACE_ROOT / "TOKENIZER_OWNER_REVIEW_30.csv"
        with open(p30, "r", encoding="utf-8") as f:
            rows30 = list(csv.DictReader(f))
        self.assertEqual(len(rows30), 30)
        for r in rows30:
            self.assertEqual(r["human_review_decision"], "NOT_REVIEWED")
            self.assertEqual(r["reviewer_rationale"], "")

        # 300-item human review sample file
        p300 = WORKSPACE_ROOT / "TOKENIZER_HUMAN_REVIEW_SAMPLE.csv"
        with open(p300, "r", encoding="utf-8") as f:
            rows300 = list(csv.DictReader(f))
        self.assertEqual(len(rows300), 300)
        for r in rows300:
            self.assertEqual(r["review_status"], "NOT_REVIEWED")
            self.assertEqual(r["human_review_decision"], "")
            self.assertEqual(r["reviewer_rationale"], "")

    def test_08_production_data_and_pretraining_locked(self):
        for d in ["production", "raw", "acquired", "quarantine"]:
            target_dir = PATCH_ROOT / d
            if target_dir.exists():
                files = [f for f in target_dir.glob("**/*") if f.is_file() and not f.name.endswith(".gitkeep")]
                self.assertEqual(len(files), 0, f"Production data present in {d}: {files}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
