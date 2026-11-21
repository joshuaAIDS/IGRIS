"""TS-LOAD tests for actual loader control flow using isolated fake backends.

These tests verify loader wiring and validation behavior without claiming that
a real trained tokenizer artifact has been supplied or loaded.
"""
import json
import sys
import tempfile
import types
from pathlib import Path
from unittest.mock import patch

from .candidate_adapters import CandidateAdapter
from .artifact_contract import (
    BACKEND_FILES, METADATA_NAME, MANIFEST_NAME, create_artifact_manifest,
)
from .metadata_contract import build_metadata
from .acceptance_config import VOCAB_SIZE, STRUCTURAL_TOKEN_IDS


def _fixture(candidate):
    root = Path(tempfile.mkdtemp(prefix="igris-loader-test-"))
    backend_name = BACKEND_FILES[candidate]
    (root / backend_name).write_bytes(b"test-double-not-a-real-tokenizer")
    (root / METADATA_NAME).write_text(
        json.dumps(build_metadata(candidate)), encoding="utf-8"
    )
    (root / MANIFEST_NAME).write_text(
        json.dumps(create_artifact_manifest(candidate, root)), encoding="utf-8"
    )
    return root


class FakeTokenizerA:
    def __init__(self, size=VOCAB_SIZE, mapping=None):
        self.size = size
        self.mapping = dict(STRUCTURAL_TOKEN_IDS if mapping is None else mapping)

    def get_vocab_size(self, with_added_tokens=True):
        return self.size

    def token_to_id(self, token):
        return self.mapping.get(token)


class FakeSentencePieceB:
    def __init__(self, size=VOCAB_SIZE, mapping=None):
        self.size = size
        self.mapping = dict(STRUCTURAL_TOKEN_IDS if mapping is None else mapping)
        self.reverse = {v: k for k, v in self.mapping.items()}

    def get_piece_size(self):
        return self.size

    def piece_to_id(self, piece):
        return self.mapping.get(piece, -1)

    def id_to_piece(self, idx):
        return self.reverse.get(idx, "<unknown>")


def run_loader_contract_tests():
    rows = []

    def record(test_id, name, fn):
        try:
            fn()
        except Exception as exc:
            rows.append((test_id, name, "FAIL", f"{type(exc).__name__}: {exc}"))
        else:
            rows.append((test_id, name, "PASS", ""))

    def expect(condition, message):
        if not condition:
            raise AssertionError(message)

    a_dir = _fixture("A")
    b_dir = _fixture("B")

    def fake_tokenizers_module(backend):
        module = types.ModuleType("tokenizers")
        class Tokenizer:
            @staticmethod
            def from_file(path):
                expect(Path(path).name == "tokenizer.json", "wrong Candidate A file")
                return backend
        module.Tokenizer = Tokenizer
        return module

    def fake_sentencepiece_module(backend):
        module = types.ModuleType("sentencepiece")
        class SentencePieceProcessor:
            def __init__(self, model_file):
                expect(Path(model_file).name == "tokenizer.model", "wrong Candidate B file")
                self._backend = backend
            def __getattr__(self, name):
                return getattr(self._backend, name)
        module.SentencePieceProcessor = SentencePieceProcessor
        return module

    record("TS-LOAD-01", "No path returns BLOCKED without loading",
           lambda: expect(CandidateAdapter("A").load().status == "BLOCKED", "expected BLOCKED"))
    def load_a():
        fake = FakeTokenizerA()
        with patch.dict(sys.modules, {"tokenizers": fake_tokenizers_module(fake)}):
            result = CandidateAdapter("A", str(a_dir)).load()
        expect(result.status == "PASS", result.reason)
        expect(result.backend is not None, "Candidate A backend missing")
    record("TS-LOAD-02", "Candidate A valid backend loads and validates", load_a)

    def load_b():
        fake = FakeSentencePieceB()
        with patch.dict(sys.modules, {"sentencepiece": fake_sentencepiece_module(fake)}):
            result = CandidateAdapter("B", str(b_dir)).load()
        expect(result.status == "PASS", result.reason)
        expect(result.backend is not None, "Candidate B backend missing")
    record("TS-LOAD-03", "Candidate B valid backend loads and validates", load_b)

    def bad_a_vocab():
        with patch.dict(sys.modules, {"tokenizers": fake_tokenizers_module(FakeTokenizerA(size=VOCAB_SIZE-1))}):
            result = CandidateAdapter("A", str(a_dir)).load()
        expect(result.status == "FAIL" and "vocabulary size mismatch" in result.reason, result.reason)
    record("TS-LOAD-04", "Candidate A rejects wrong vocabulary size", bad_a_vocab)

    def bad_b_vocab():
        with patch.dict(sys.modules, {"sentencepiece": fake_sentencepiece_module(FakeSentencePieceB(size=VOCAB_SIZE-1))}):
            result = CandidateAdapter("B", str(b_dir)).load()
        expect(result.status == "FAIL" and "vocabulary size mismatch" in result.reason, result.reason)
    record("TS-LOAD-05", "Candidate B rejects wrong vocabulary size", bad_b_vocab)

    def bad_a_ids():
        mapping = dict(STRUCTURAL_TOKEN_IDS)
        mapping["<|assistant|>"] = 13
        with patch.dict(sys.modules, {"tokenizers": fake_tokenizers_module(FakeTokenizerA(mapping=mapping))}):
            result = CandidateAdapter("A", str(a_dir)).load()
        expect(result.status == "FAIL" and "structural ID mismatch" in result.reason, result.reason)
    record("TS-LOAD-06", "Candidate A rejects incorrect structural IDs", bad_a_ids)

    def bad_b_ids():
        mapping = dict(STRUCTURAL_TOKEN_IDS)
        mapping["<|assistant|>"] = 13
        with patch.dict(sys.modules, {"sentencepiece": fake_sentencepiece_module(FakeSentencePieceB(mapping=mapping))}):
            result = CandidateAdapter("B", str(b_dir)).load()
        expect(result.status == "FAIL" and "structural ID mismatch" in result.reason, result.reason)
    record("TS-LOAD-07", "Candidate B rejects incorrect structural IDs", bad_b_ids)

    def invalid_manifest():
        (a_dir / MANIFEST_NAME).write_text("{broken", encoding="utf-8")
        result = CandidateAdapter("A", str(a_dir)).load()
        expect(result.status == "FAIL" and "Artifact contract" in result.reason, result.reason)
    record("TS-LOAD-08", "Invalid artifact manifest fails before backend import", invalid_manifest)

    def invalid_candidate():
        try:
            CandidateAdapter("C")
        except ValueError:
            return
        raise AssertionError("unsupported candidate accepted")
    record("TS-LOAD-09", "Reject unsupported candidate selector", invalid_candidate)

    return rows


if __name__ == "__main__":
    rows = run_loader_contract_tests()
    for test_id, name, status, detail in rows:
        print(f"{test_id:14} {status:4} {name}")
        if detail:
            print("   ", detail)
    passed = sum(row[2] == "PASS" for row in rows)
    failed = len(rows) - passed
    print(f"TOTAL: {len(rows)} | PASS: {passed} | FAIL: {failed}")
    raise SystemExit(1 if failed else 0)
