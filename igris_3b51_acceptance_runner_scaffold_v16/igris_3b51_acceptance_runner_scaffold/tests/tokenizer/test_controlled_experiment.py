"""Unit tests for the non-training controlled experiment planner/auditor."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path

from .controlled_experiment import build_experiment_plan, plan_to_dict, write_plan, compare_artifact_pair


class ControlledExperimentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.corpus = self.root / "prepared.txt"
        self.corpus.write_text("hello\nவணக்கம்\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_plan_has_two_runs_per_candidate(self):
        plan = build_experiment_plan([self.corpus], self.root / "runs")
        data = plan_to_dict(plan)
        self.assertEqual([r["run"] for r in data["candidates"]["A"]["runs"]], [1, 2])
        self.assertEqual([r["run"] for r in data["candidates"]["B"]["runs"]], [1, 2])

    def test_plan_never_claims_training_executed(self):
        plan = build_experiment_plan([self.corpus], self.root / "runs")
        self.assertIn("NOT_EXECUTED", plan.training_execution)

    def test_same_corpus_fingerprint_shared(self):
        plan = build_experiment_plan([self.corpus], self.root / "runs")
        self.assertEqual(len(plan.corpus), 1)
        self.assertEqual(len(plan.corpus[0][1]), 64)

    def test_empty_corpus_list_rejected(self):
        with self.assertRaises(ValueError):
            build_experiment_plan([], self.root / "runs")

    def test_missing_corpus_rejected(self):
        with self.assertRaises(FileNotFoundError):
            build_experiment_plan([self.root / "missing.txt"], self.root / "runs")

    def test_empty_corpus_file_rejected(self):
        empty = self.root / "empty.txt"
        empty.write_bytes(b"")
        with self.assertRaises(ValueError):
            build_experiment_plan([empty], self.root / "runs")

    def test_plan_json_round_trip(self):
        plan = build_experiment_plan([self.corpus], self.root / "runs")
        path = write_plan(plan, self.root / "plan.json")
        parsed = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(parsed["schema_version"], "1.0")

    def test_output_paths_are_separate(self):
        data = plan_to_dict(build_experiment_plan([self.corpus], self.root / "runs"))
        a1 = data["candidates"]["A"]["runs"][0]["output_dir"]
        a2 = data["candidates"]["A"]["runs"][1]["output_dir"]
        b1 = data["candidates"]["B"]["runs"][0]["output_dir"]
        self.assertEqual(len({a1, a2, b1}), 3)

    def test_artifact_pair_identical(self):
        a, b = self.root / "a.bin", self.root / "b.bin"
        a.write_bytes(b"same"); b.write_bytes(b"same")
        result = compare_artifact_pair(a, b)
        self.assertTrue(result["identical_bytes"])

    def test_artifact_pair_different(self):
        a, b = self.root / "a.bin", self.root / "b.bin"
        a.write_bytes(b"one"); b.write_bytes(b"two")
        result = compare_artifact_pair(a, b)
        self.assertFalse(result["identical_bytes"])

    def test_artifact_missing_rejected(self):
        with self.assertRaises(FileNotFoundError):
            compare_artifact_pair(self.root / "missing", self.root / "also_missing")


if __name__ == "__main__":
    unittest.main()
