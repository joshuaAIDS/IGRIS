"""
IGRIS Phase 21A - Tokenizer Selection Record & Dataset Review Test Suite
Operating Model: SOLO_DEVELOPER_OWNER_REVIEW

Verifies:
1. Tokenizer Candidate A and B physical file hashes and immutability.
2. Tokenizer selection governance records (Markdown and JSON audit).
3. Dataset authorization review records (18 sources, 13 approved for consideration, 5 on hold).
4. Production gates locked and zero production ingress.
5. Quarantine filename isolation.
"""

import csv
import hashlib
import json
import os
import sys
import pytest

PATCH_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PATCH_ROOT)
sys.path.insert(0, os.path.join(PATCH_ROOT, "src"))
sys.path.insert(0, os.path.join(PATCH_ROOT, "scripts"))

from secure_acquisition_engine import SecureAcquisitionEngine


def hash_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestPhase21ATokenizerSelectionAndDatasetReview:
    """Rigorous verification of Phase 21A deliverables and governance controls."""

    def test_01_tokenizer_physical_hashes(self):
        """Verify Candidate A and Candidate B match exact canonical digests."""
        cand_a_path = os.path.join(PATCH_ROOT, "artifacts", "tokenizer", "candidate_a", "tokenizer.json")
        cand_b_path = os.path.join(PATCH_ROOT, "artifacts", "tokenizer", "candidate_b", "tokenizer.model")

        assert hash_file(cand_a_path) == "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
        assert hash_file(cand_b_path) == "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

    def test_02_tokenizer_selection_records(self):
        """Verify Tokenizer Selection Record and Owner Decision Audit JSON."""
        rec_md = os.path.join(PATCH_ROOT, "PHASE21A_TOKENIZER_SELECTION_RECORD.md")
        audit_json = os.path.join(PATCH_ROOT, "PHASE21A_OWNER_DECISION_AUDIT.json")
        integ_md = os.path.join(PATCH_ROOT, "PHASE21A_TOKENIZER_INTEGRITY_REPORT.md")

        assert os.path.isfile(rec_md)
        assert os.path.isfile(audit_json)
        assert os.path.isfile(integ_md)

        with open(rec_md, "r", encoding="utf-8") as f:
            content = f.read()
            assert "Candidate A" in content
            assert "ByteLevel BPE" in content
            assert "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561" in content

        with open(audit_json, "r", encoding="utf-8") as f:
            audit = json.load(f)
            assert audit["decision_summary"]["selected_candidate"] == "Candidate A"
            assert audit["decision_summary"]["selected_architecture"] == "ByteLevel BPE"
            assert audit["decision_summary"]["selected_file_sha256"] == "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
            assert audit["audit_metadata"]["decision_maker"] == "SOLE_DEVELOPER_PROJECT_OWNER"
            assert audit["audit_metadata"]["independent_reviewers_fabricated"] is False

    def test_03_dataset_authorization_review(self):
        """Verify Dataset Authorization Review ledger (18 sources, 13 approve, 5 hold)."""
        review_csv = os.path.join(PATCH_ROOT, "PHASE21A_DATASET_AUTHORIZATION_REVIEW.csv")
        review_md = os.path.join(PATCH_ROOT, "PHASE21A_DATASET_AUTHORIZATION_REVIEW.md")

        assert os.path.isfile(review_csv)
        assert os.path.isfile(review_md)

        with open(review_csv, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert len(rows) == 18

        approved = [r for r in rows if r["recommended_decision"] == "APPROVE FOR OWNER CONSIDERATION"]
        held = [r for r in rows if r["recommended_decision"] == "HOLD"]

        assert len(approved) == 13, f"Expected 13 approved, got {len(approved)}"
        assert len(held) == 5, f"Expected 5 on hold, got {len(held)}"

        held_ids = {r["source_id"] for r in held}
        assert held_ids == {"SRC-EN-01", "SRC-CV-06", "SRC-TG-01", "SRC-TG-02", "SRC-CD-01"}

    def test_04_governance_controls_and_gate_locked(self):
        """Verify production ingress gate locked and isolation invariant."""
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmpdir:
            isolated_audit = Path(tmpdir) / "acquisition_audit.jsonl"
            engine = SecureAcquisitionEngine(audit_log_path=isolated_audit)
            assert not engine.is_gate_unlocked()

        for root, dirs, files in os.walk(PATCH_ROOT):
            for f in files:
                if not f.endswith(".md"):
                    assert "quarantine" not in f.lower(), f"Isolation violation: {os.path.join(root, f)}"
