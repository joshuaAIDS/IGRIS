"""
IGRIS Phase 21 - Controlled Production Dataset Preparation Test Suite
Operating Model: SOLO_DEVELOPER_OWNER_REVIEW

Verifies:
1. Tokenizer candidate physical file hashes and immutability.
2. Complete 18-source license review integrity (no share-alike, permissive only).
3. Owner authorization register integrity (18 pending, 0 authorized).
4. Controlled acquisition ledger integrity (0 acquired bytes, quarantine empty).
5. Dataset manifest and multilingual statistics consistency.
6. Filename isolation invariant.
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

from secure_acquisition_engine import SecureAcquisitionEngine, AcquisitionGateLockedError


def hash_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestPhase21ControlledDatasetPreparation:
    """Rigorous verification of Phase 21 deliverables and governance invariants."""

    def test_01_tokenizer_candidate_immutability(self):
        """Verify physical tokenizer files match canonical hashes."""
        cand_a_path = os.path.join(PATCH_ROOT, "artifacts", "tokenizer", "candidate_a", "tokenizer.json")
        cand_b_path = os.path.join(PATCH_ROOT, "artifacts", "tokenizer", "candidate_b", "tokenizer.model")

        assert hash_file(cand_a_path) == "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
        assert hash_file(cand_b_path) == "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

    def test_02_source_license_review_eighteen_sources(self):
        """Verify all 18 eligible sources reviewed without share-alike obligations."""
        lic_file = os.path.join(PATCH_ROOT, "PHASE21_SOURCE_LICENSE_REVIEW.csv")
        assert os.path.isfile(lic_file)

        with open(lic_file, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert len(rows) == 18, f"Expected 18 sources, got {len(rows)}"

        for r in rows:
            assert r["eligible_classification_status"] == "ELIGIBLE"
            assert r["commercial_use_permission"] == "YES"
            assert r["share_alike_obligations"] == "NONE"
            assert "explicit individual owner authorization" in r["owner_authorization_prerequisite"]

    def test_03_owner_authorization_register_zero_authorized(self):
        """Verify owner authorization register has all 18 pending, 0 authorized."""
        auth_file = os.path.join(PATCH_ROOT, "PHASE21_OWNER_AUTHORIZATION_REGISTER.csv")
        assert os.path.isfile(auth_file)

        with open(auth_file, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert len(rows) == 18

        for r in rows:
            assert r["authorization_status"] == "PENDING_EXPLICIT_OWNER_AUTHORIZATION"
            assert r["owner_approval_reference"] == "NONE_AWAITING_OWNER_KEY_SIGNATURE"
            assert r["authorization_timestamp"] == "NONE"
            assert r["governance_model"] == "SOLO_DEVELOPER_OWNER_REVIEW"

    def test_04_acquisition_ledger_zero_acquired(self):
        """Verify acquisition ledger contains zero acquired records."""
        acq_file = os.path.join(PATCH_ROOT, "PHASE21_ACQUISITION_LEDGER.csv")
        assert os.path.isfile(acq_file)

        with open(acq_file, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert len(rows) == 0, f"Expected 0 acquired records, got {len(rows)}"

    def test_05_dataset_manifest_and_multilingual_statistics(self):
        """Verify manifest JSON and multilingual statistics CSV."""
        manifest_file = os.path.join(PATCH_ROOT, "PHASE21_DATASET_MANIFEST.json")
        stats_file = os.path.join(PATCH_ROOT, "PHASE21_MULTILINGUAL_STATISTICS.csv")

        assert os.path.isfile(manifest_file)
        assert os.path.isfile(stats_file)

        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["governance_summary"]["eligible_candidate_sources"] == 18
        assert manifest["governance_summary"]["explicitly_authorized_sources"] == 0
        assert manifest["governance_summary"]["acquired_production_bytes"] == 0
        assert manifest["manifest_metadata"]["production_ingress_gate"] == "LOCKED"

        with open(stats_file, "r", encoding="utf-8") as f:
            stats = list(csv.DictReader(f))

        assert len(stats) == 18
        total_projected_clean_tokens = sum(int(r["projected_clean_tokens_candidate_a"]) for r in stats)
        assert total_projected_clean_tokens > 10_000_000_000, f"Projected tokens: {total_projected_clean_tokens}"

        for r in stats:
            assert r["data_nature"] == "PUBLISHED_CATALOG_ESTIMATE"
            assert int(r["actual_acquired_production_bytes"]) == 0
            assert int(r["actual_acquired_production_records"]) == 0

    def test_06_gate_locked_and_filename_isolation(self):
        """Verify acquisition engine gate locked and filename isolation."""
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
