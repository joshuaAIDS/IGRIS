import tempfile
import unittest
from pathlib import Path
from .reproducibility import (RunRecord, build_run_record, compare_runs,
    environment_fingerprint, reproducibility_policy, sha256_file)

class ReproducibilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        self.artifact = self.root / "artifact.bin"; self.artifact.write_bytes(b"synthetic-artifact")
        self.env = environment_fingerprint(tokenizers_version="0.23.3", sentencepiece_version="0.2.3")
        self.config = {"vocab_size": 32768, "input_order": ["a.txt"], "threads": 1}
        self.corpus_hash = "a" * 64
    def tearDown(self): self.tmp.cleanup()
    def record(self, candidate="A"):
        return build_run_record(candidate, self.corpus_hash, self.config, self.env, self.artifact)
    def test_01_candidate_a_empirical_only(self):
        p = reproducibility_policy("A"); self.assertEqual(p["level"], "EMPIRICAL_ONLY"); self.assertFalse(p["seed_control"])
    def test_02_candidate_b_requires_empirical_verification(self):
        p = reproducibility_policy("B"); self.assertEqual(p["level"], "CONTROLLED_BUT_EMPIRICAL_REQUIRED")
    def test_03_unknown_policy_rejected(self):
        with self.assertRaises(ValueError): reproducibility_policy("C")
    def test_04_environment_fingerprint(self):
        self.assertTrue(self.env["python"]); self.assertTrue(self.env["platform"])
    def test_05_file_hash(self): self.assertEqual(len(sha256_file(self.artifact)), 64)
    def test_06_missing_artifact_rejected(self):
        with self.assertRaises(FileNotFoundError): sha256_file(self.root / "missing")
    def test_07_identical_runs_pass(self): self.assertTrue(compare_runs(self.record(), self.record())[0])
    def test_08_artifact_hash_mismatch_fails(self):
        a = self.record(); b = RunRecord(a.candidate, a.corpus_sha256, a.config_sha256, a.environment, "b"*64)
        self.assertFalse(compare_runs(a,b)[0])
    def test_09_environment_mismatch_fails(self):
        a = self.record("B"); b = RunRecord(a.candidate,a.corpus_sha256,a.config_sha256,{**a.environment,"python":"0"},a.artifact_sha256)
        self.assertFalse(compare_runs(a,b)[0])
    def test_10_candidate_mismatch_fails(self):
        a = self.record(); b = RunRecord("B",a.corpus_sha256,a.config_sha256,a.environment,a.artifact_sha256)
        self.assertFalse(compare_runs(a,b)[0])
    def test_11_invalid_corpus_hash_rejected(self):
        with self.assertRaises(ValueError): build_run_record("A","bad",self.config,self.env,self.artifact)
    def test_12_invalid_candidate_rejected(self):
        with self.assertRaises(ValueError): build_run_record("C",self.corpus_hash,self.config,self.env,self.artifact)
    def test_13_non_mapping_config_rejected(self):
        with self.assertRaises(TypeError): build_run_record("A",self.corpus_hash,[],self.env,self.artifact)
    def test_14_artifact_change_changes_hash(self):
        old=sha256_file(self.artifact); self.artifact.write_bytes(b"changed"); self.assertNotEqual(old,sha256_file(self.artifact))
    def test_15_corpus_mismatch_fails(self):
        a=self.record(); b=RunRecord(a.candidate,"c"*64,a.config_sha256,a.environment,a.artifact_sha256)
        self.assertFalse(compare_runs(a,b)[0])
if __name__ == "__main__": unittest.main()
