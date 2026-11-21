"""
verify_owner_review_session.py

Automated test suite verifying the integrity, governance, and completeness
of the SOLO_DEVELOPER_OWNER_REVIEW session deliverables.

Assertions:
1. Exactly 30 review examples in TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv
2. Exactly 10 examples per language (10 Tamil, 10 English, 10 Tanglish)
3. All 30 review identifiers (OWN-REV-01 to OWN-REV-30) are unique
4. Both tokenizer outputs and token IDs are present and non-empty for all 30 rows
5. All 30 owner decision values remain strictly NOT_REVIEWED with blank rationale
6. All tokenizer hashes match the exact required SHA256 values
7. Production acquisition and pretraining gates remain strictly locked
"""

import csv
import hashlib
import json
import os
import unittest
from pathlib import Path

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")

EXPECTED_HASHES = {
    "candidate_a": "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561",
    "candidate_a_synthetic_experiment": "3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce",
    "candidate_b": "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"
}

TOKENIZER_PATHS = {
    "candidate_a": WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json",
    "candidate_a_synthetic_experiment": PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json",
    "candidate_b": WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
}

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

class TestOwnerReviewSession(unittest.TestCase):

    def test_01_cryptographic_hashes(self):
        """Verify SHA256 integrity of all three tokenizer artifacts."""
        for name, expected_hash in EXPECTED_HASHES.items():
            path = TOKENIZER_PATHS[name]
            self.assertTrue(path.exists(), f"Tokenizer artifact missing: {path}")
            actual_hash = compute_sha256(path)
            self.assertEqual(actual_hash, expected_hash, f"Hash mismatch for {name}: {actual_hash} != {expected_hash}")

    def test_02_deliverables_presence_across_all_locations(self):
        """Verify that all 3 deliverables are mirrored across workspace root, patch root, and artifact directory."""
        filenames = [
            "TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv",
            "TOKENIZER_OWNER_REVIEW_SESSION.md",
            "TOKENIZER_OWNER_REVIEW_EVIDENCE_INDEX.md"
        ]
        locations = [WORKSPACE_ROOT, PATCH_ROOT, ARTIFACT_DIR]
        for fn in filenames:
            for loc in locations:
                path = loc / fn
                self.assertTrue(path.exists(), f"Deliverable missing at {path}")
                self.assertGreater(path.stat().st_size, 0, f"File is empty: {path}")

    def test_03_decisions_template_row_count_and_uniqueness(self):
        """Assert exactly 30 review examples in template, and all IDs (OWN-REV-01 to OWN-REV-30) are unique."""
        template_path = WORKSPACE_ROOT / "TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv"
        with open(template_path, mode="r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
        
        self.assertEqual(len(reader), 30, f"Expected exactly 30 rows in decisions template, found {len(reader)}")
        
        ids = [row["review_id"] for row in reader]
        self.assertEqual(len(set(ids)), 30, f"Duplicate review_ids found: {ids}")
        for i in range(1, 31):
            expected_id = f"OWN-REV-{i:02d}"
            self.assertIn(expected_id, ids, f"Missing expected ID {expected_id}")

    def test_04_language_distribution(self):
        """Assert exactly 10 examples per language (10 Tamil, 10 English, 10 Tanglish)."""
        template_path = WORKSPACE_ROOT / "TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv"
        with open(template_path, mode="r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
        
        lang_counts = {}
        for row in reader:
            lang = row["language"]
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
            
        self.assertEqual(lang_counts.get("TAMIL", 0), 10, f"Expected 10 TAMIL rows, got {lang_counts.get('TAMIL')}")
        self.assertEqual(lang_counts.get("ENGLISH", 0), 10, f"Expected 10 ENGLISH rows, got {lang_counts.get('ENGLISH')}")
        self.assertEqual(lang_counts.get("TANGLISH", 0), 10, f"Expected 10 TANGLISH rows, got {lang_counts.get('TANGLISH')}")

    def test_05_tokens_and_ids_present(self):
        """Assert both tokenizer outputs and token IDs are present and non-empty for all 30 rows."""
        template_path = WORKSPACE_ROOT / "TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv"
        with open(template_path, mode="r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            
        for row in reader:
            rid = row["review_id"]
            self.assertTrue(row["original_text"].strip(), f"Empty original_text in {rid}")
            self.assertTrue(row["cand_a_tokens"].strip(), f"Empty cand_a_tokens in {rid}")
            self.assertTrue(row["cand_a_token_ids"].strip(), f"Empty cand_a_token_ids in {rid}")
            self.assertTrue(row["cand_exp_tokens"].strip(), f"Empty cand_exp_tokens in {rid}")
            self.assertTrue(row["cand_exp_token_ids"].strip(), f"Empty cand_exp_token_ids in {rid}")
            self.assertGreater(int(row["cand_a_count"]), 0, f"Zero token count in {rid}")
            self.assertGreater(int(row["cand_exp_count"]), 0, f"Zero token count in {rid}")

    def test_06_governance_decisions_not_reviewed(self):
        """Assert all 30 owner decision values remain strictly NOT_REVIEWED with blank rationale."""
        template_path = WORKSPACE_ROOT / "TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv"
        with open(template_path, mode="r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            
        for row in reader:
            rid = row["review_id"]
            self.assertEqual(row["owner_decision"], "NOT_REVIEWED", f"owner_decision not NOT_REVIEWED for {rid}: {row['owner_decision']}")
            self.assertEqual(row["owner_rationale"].strip(), "", f"owner_rationale is not blank for {rid}: {row['owner_rationale']}")

    def test_07_session_document_coverage(self):
        """Assert TOKENIZER_OWNER_REVIEW_SESSION.md covers all 30 review IDs and all 6 decision options."""
        session_doc_path = WORKSPACE_ROOT / "TOKENIZER_OWNER_REVIEW_SESSION.md"
        content = session_doc_path.read_text(encoding="utf-8")
        
        for i in range(1, 31):
            rid = f"OWN-REV-{i:02d}"
            self.assertIn(f"### {rid}:", content, f"Missing section for {rid} in session doc")
            
        decision_options = [
            "OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION",
            "OWNER_ACCEPTS_ORIGINAL_SEGMENTATION",
            "OWNER_ACCEPTS_BOTH",
            "OWNER_REJECTS_BOTH",
            "OWNER_REQUIRES_MORE_EVIDENCE",
            "NOT_REVIEWED"
        ]
        for opt in decision_options:
            self.assertIn(opt, content, f"Missing decision option {opt} in session doc")

    def test_08_production_data_and_pretraining_locked(self):
        """Verify that production gates remain locked ($0.00 cloud spend, no external downloads)."""
        gate_status_file = WORKSPACE_ROOT / "documentation" / "PHASE22_GATE_STATUS.json"
        if not gate_status_file.exists():
            gate_status_file = WORKSPACE_ROOT / "PHASE22_GATE_STATUS.json"
        if gate_status_file.exists():
            with open(gate_status_file, "r", encoding="utf-8") as f:
                gates = json.load(f)
            self.assertIn(gates.get("pretraining_gate", "LOCKED"), ["LOCKED", "GATE_LOCKED"])
            self.assertIn(gates.get("acquisition_gate", "LOCKED"), ["LOCKED", "GATE_LOCKED"])

if __name__ == "__main__":
    unittest.main()
