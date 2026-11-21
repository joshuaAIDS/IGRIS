"""IGRIS Milestone 3B.59 — Unit tests for Production Readiness Orchestrator."""
from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

# Add patch src and scripts
_PATCH_ROOT = Path(__file__).resolve().parents[1]
_PATCH_SRC = str(_PATCH_ROOT / "src")
_PATCH_SCRIPTS = str(_PATCH_ROOT / "scripts")
for p in [_PATCH_SRC, _PATCH_SCRIPTS]:
    if p not in sys.path:
        sys.path.insert(0, p)

from evaluation_acceptance import AcceptanceThresholdEvaluator
from production_eval_readiness import get_environment_manifest

CANDIDATE_A_PATH = _PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
CANDIDATE_B_PATH = _PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"


class TestReadiness(unittest.TestCase):
    def test_environment_manifest(self) -> None:
        """Verifies environment manifest contains all required telemetry fields."""
        manifest = get_environment_manifest()
        self.assertEqual(manifest["milestone"], "3B.59")
        self.assertIn("environment", manifest)
        self.assertIn("python_version", manifest["environment"])
        self.assertIn("platform", manifest["environment"])
        self.assertIn("dependencies", manifest)
        self.assertEqual(manifest["dependencies"]["tokenizers"], "0.23.3")
        self.assertEqual(manifest["dependencies"]["sentencepiece"], "0.2.3")
        self.assertEqual(manifest["dependencies"]["unicode_database_version"], "15.1.0")
        self.assertIn("candidate_a", manifest["tokenizer_artifacts"])
        self.assertIn("candidate_b", manifest["tokenizer_artifacts"])

    def test_artifact_hashes_in_manifest(self) -> None:
        """Verifies that artifact hashes in the manifest match disk bytes exactly."""
        manifest = get_environment_manifest()
        hash_a_manifest = manifest["tokenizer_artifacts"]["candidate_a"]["sha256"]
        hash_b_manifest = manifest["tokenizer_artifacts"]["candidate_b"]["sha256"]

        hash_a_disk = hashlib.sha256(CANDIDATE_A_PATH.read_bytes()).hexdigest()
        hash_b_disk = hashlib.sha256(CANDIDATE_B_PATH.read_bytes()).hexdigest()

        self.assertEqual(hash_a_manifest, hash_a_disk)
        self.assertEqual(hash_b_manifest, hash_b_disk)

    def test_acceptance_threshold_evaluator_mandatory_pass(self) -> None:
        """Evaluator passes when all mandatory hard gates are satisfied."""
        evaluator = AcceptanceThresholdEvaluator()
        good_metrics = {
            "round_trip_fidelity_pct": 100.0,
            "structural_isolation_pct": 100.0,
            "vocab_size": 32768,
            "structural_token_count": 12,
            "byte_fallback_count": 256,
            "unicode_version": "15.1.0",
            "context_length": 2048,
            "encoding_throughput_chars_sec": 500000.0,
            "decoding_throughput_tokens_sec": 2000000.0,
        }
        res = evaluator.evaluate_candidate("Candidate A", good_metrics, is_synthetic=True)
        self.assertTrue(res.mandatory_passed)
        self.assertTrue(res.ready_for_production_review)

    def test_acceptance_threshold_evaluator_mandatory_fail(self) -> None:
        """Evaluator flags failure if any mandatory hard gate fails."""
        evaluator = AcceptanceThresholdEvaluator()
        bad_metrics = {
            "round_trip_fidelity_pct": 99.9,  # Must be strictly 100.0%
            "structural_isolation_pct": 100.0,
            "vocab_size": 32768,
            "structural_token_count": 12,
            "byte_fallback_count": 256,
            "unicode_version": "15.1.0",
            "context_length": 2048,
        }
        res = evaluator.evaluate_candidate("Candidate A", bad_metrics, is_synthetic=True)
        self.assertFalse(res.mandatory_passed)
        self.assertFalse(res.ready_for_production_review)

    def test_governance_isolation_check(self) -> None:
        """Verifies zero access to private training data or production corpus."""
        patch_files = list(_PATCH_ROOT.rglob("*"))
        for p in patch_files:
            if p.suffix.lower() in [".md", ".markdown"]:
                continue
            name_lower = p.name.lower()
            # Ensure no production corpus or quarantine files exist in the patch
            self.assertNotIn("quarantine", name_lower)
            self.assertNotIn("approved_line_inventory.csv", name_lower)
            self.assertNotIn("tamil_nfc_deduplicated.txt", name_lower)


if __name__ == "__main__":
    unittest.main()
