"""TS-META shared metadata validation and save/reload contract tests."""
import json
import tempfile
from pathlib import Path

from .metadata_contract import (
    build_metadata, validate_metadata, serialize_metadata,
    save_metadata, load_metadata,
)


def run_metadata_contract_tests():
    rows = []

    def record(test_id, name, fn):
        try:
            fn()
        except Exception as exc:
            rows.append((test_id, name, "FAIL",
                         f"{type(exc).__name__}: {exc}"))
        else:
            rows.append((test_id, name, "PASS", ""))

    def eq(actual, expected):
        if actual != expected:
            raise AssertionError(f"{actual!r} != {expected!r}")

    def rejects(fn, expected):
        try:
            fn()
        except expected:
            return
        raise AssertionError(f"Expected {expected.__name__}")

    a = build_metadata("A")
    b = build_metadata("B")

    record("TS-META-01", "Candidate A metadata has all required fields",
           lambda: validate_metadata(a))
    record("TS-META-02", "Candidate B metadata has all required fields",
           lambda: validate_metadata(b))
    record("TS-META-03", "Candidate A identity and algorithm are consistent",
           lambda: (eq(a["candidate"], "A"), eq(a["algorithm"], "bytelevel_bpe")))
    record("TS-META-04", "Candidate B identity and algorithm are consistent",
           lambda: (eq(b["candidate"], "B"), eq(b["algorithm"], "sentencepiece_unigram")))
    record("TS-META-05", "Vocabulary size is exactly 32768",
           lambda: (eq(a["vocab_size"], 32768), eq(b["vocab_size"], 32768)))
    record("TS-META-06", "Structural token list preserves fixed order",
           lambda: eq(a["structural_tokens"], [
               "<|pad|>", "<|begin_of_text|>", "<|end_of_text|>", "<think>",
               "</think>", "<action>", "</action>", "<action_result>",
               "</action_result>", "<|system|>", "<|user|>", "<|assistant|>"
           ]))
    record("TS-META-07", "Structural token IDs are fixed from 0 through 11",
           lambda: eq(list(a["structural_token_ids"].values()), list(range(12))))
    record("TS-META-08", "Reject missing required metadata field",
           lambda: rejects(lambda: validate_metadata({k:v for k,v in a.items()
                                                       if k != "vocab_size"}), ValueError))
    record("TS-META-09", "Reject incomplete structural token list",
           lambda: rejects(lambda: validate_metadata({**a, "structural_tokens": a["structural_tokens"][:-1]}), ValueError))
    record("TS-META-10", "Reject reordered structural token IDs",
           lambda: rejects(lambda: validate_metadata({**a, "structural_token_ids": {
               **a["structural_token_ids"], "<|user|>": 9, "<|system|>": 10
           }}), ValueError))
    record("TS-META-11", "Reject incorrect vocabulary size",
           lambda: rejects(lambda: validate_metadata({**a, "vocab_size": 32000}), ValueError))
    record("TS-META-12", "Reject candidate/algorithm mismatch",
           lambda: rejects(lambda: validate_metadata({**a, "algorithm": "sentencepiece_unigram"}), ValueError))
    record("TS-META-13", "Reject unsupported metadata schema version",
           lambda: rejects(lambda: validate_metadata({**a, "metadata_schema_version": "9.9"}), ValueError))
    record("TS-META-14", "Reject project version mismatch",
           lambda: rejects(lambda: validate_metadata({**a, "project_version": "old"}), ValueError))
    record("TS-META-15", "Reject Unicode version mismatch",
           lambda: rejects(lambda: validate_metadata({**a, "unicode_version": "14.0.0"}), ValueError))
    record("TS-META-16", "Reject non-object metadata",
           lambda: rejects(lambda: validate_metadata(["not", "an", "object"]), TypeError))
    record("TS-META-17", "Canonical serialization is deterministic",
           lambda: eq(serialize_metadata(a), serialize_metadata(dict(reversed(list(a.items()))))))
    record("TS-META-18", "Save and reload preserves Candidate A metadata",
           lambda: (lambda p: (save_metadata(p, a), eq(load_metadata(p), a)))(Path(tempfile.mktemp(suffix=".json"))))
    record("TS-META-19", "Save and reload preserves Candidate B metadata",
           lambda: (lambda p: (save_metadata(p, b), eq(load_metadata(p), b)))(Path(tempfile.mktemp(suffix=".json"))))
    record("TS-META-20", "Reject malformed JSON metadata file",
           lambda: (lambda p: (p.write_text("{broken", encoding="utf-8"),
                               rejects(lambda: load_metadata(p), ValueError)))(Path(tempfile.mktemp(suffix=".json"))))
    record("TS-META-21", "Reject valid JSON with missing required field",
           lambda: (lambda p: (p.write_text(json.dumps({"project": "IGRIS"}), encoding="utf-8"),
                               rejects(lambda: load_metadata(p), ValueError)))(Path(tempfile.mktemp(suffix=".json"))))
    record("TS-META-22", "Reject NaN during deterministic serialization",
           lambda: rejects(lambda: serialize_metadata({**a, "extension": float("nan")}), ValueError))
    record("TS-META-23", "Allow non-conflicting extension metadata",
           lambda: eq(build_metadata("A", extra={"trainer_note": "synthetic"})["trainer_note"], "synthetic"))
    record("TS-META-24", "Reject extension override of required field",
           lambda: rejects(lambda: build_metadata("A", extra={"vocab_size": 10}), ValueError))

    return rows


if __name__ == "__main__":
    rows = run_metadata_contract_tests()
    for test_id, name, status, detail in rows:
        print(f"{test_id:14} {status:4} {name}")
        if detail:
            print("   ", detail)
    passed = sum(row[2] == "PASS" for row in rows)
    failed = len(rows) - passed
    print(f"TOTAL: {len(rows)} | PASS: {passed} | FAIL: {failed}")
    raise SystemExit(1 if failed else 0)
