"""TS-ART shared artifact directory/interface contract tests."""
import json
import tempfile
from pathlib import Path

from .artifact_contract import (
    MANIFEST_NAME, METADATA_NAME, BACKEND_FILES,
    ArtifactContractError, create_artifact_manifest, validate_artifact_directory,
)
from .metadata_contract import build_metadata


def run_artifact_contract_tests():
    rows = []

    def record(test_id, name, fn):
        try:
            fn()
        except Exception as exc:
            rows.append((test_id, name, "FAIL", f"{type(exc).__name__}: {exc}"))
        else:
            rows.append((test_id, name, "PASS", ""))

    def make_fixture(candidate="A"):
        root = Path(tempfile.mkdtemp(prefix="igris-artifact-contract-"))
        (root / BACKEND_FILES[candidate]).write_bytes(b"synthetic-backend-placeholder")
        (root / METADATA_NAME).write_text(
            json.dumps(build_metadata(candidate), ensure_ascii=False), encoding="utf-8"
        )
        manifest = create_artifact_manifest(candidate, root)
        (root / MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")
        return root

    def rejects(fn):
        try:
            fn()
        except ArtifactContractError:
            return
        raise AssertionError("Expected ArtifactContractError")

    a = make_fixture("A")
    b = make_fixture("B")

    record("TS-ART-01", "Accept valid Candidate A artifact directory",
           lambda: validate_artifact_directory("A", a))
    record("TS-ART-02", "Accept valid Candidate B artifact directory",
           lambda: validate_artifact_directory("B", b))
    record("TS-ART-03", "Require directory path, not a single file",
           lambda: rejects(lambda: validate_artifact_directory("A", a / BACKEND_FILES["A"])))
    record("TS-ART-04", "Reject nonexistent artifact directory",
           lambda: rejects(lambda: validate_artifact_directory("A", a / "missing")))
    def reject_after_removal(candidate, filename):
        root = make_fixture(candidate)
        (root / filename).unlink()
        rejects(lambda: validate_artifact_directory(candidate, root))

    record("TS-ART-05", "Reject missing backend artifact",
           lambda: reject_after_removal("A", BACKEND_FILES["A"]))
    record("TS-ART-06", "Reject missing metadata file",
           lambda: reject_after_removal("A", METADATA_NAME))
    record("TS-ART-07", "Reject missing artifact manifest",
           lambda: reject_after_removal("A", MANIFEST_NAME))
    record("TS-ART-08", "Reject empty backend artifact",
           lambda: (lambda p: ((p / BACKEND_FILES["A"]).write_bytes(b""),
                               rejects(lambda: validate_artifact_directory("A", p))))(make_fixture("A")))
    record("TS-ART-09", "Reject corrupt manifest JSON",
           lambda: (lambda p: ((p / MANIFEST_NAME).write_text("{bad", encoding="utf-8"),
                               rejects(lambda: validate_artifact_directory("A", p))))(make_fixture("A")))
    record("TS-ART-10", "Reject wrong candidate identity in manifest",
           lambda: (lambda p: ((lambda m: (m.update(candidate="B"),
                               (p / MANIFEST_NAME).write_text(json.dumps(m))))(
                                   json.loads((p / MANIFEST_NAME).read_text())),
                               rejects(lambda: validate_artifact_directory("A", p))))(make_fixture("A")))
    record("TS-ART-11", "Reject Candidate A/B backend filename mismatch",
           lambda: rejects(lambda: validate_artifact_directory("B", a)))
    record("TS-ART-12", "Reject project version mismatch",
           lambda: (lambda p: ((lambda m: (m.update(project_version="old"),
                               (p / MANIFEST_NAME).write_text(json.dumps(m))))(
                                   json.loads((p / MANIFEST_NAME).read_text())),
                               rejects(lambda: validate_artifact_directory("A", p))))(make_fixture("A")))
    record("TS-ART-13", "Reject metadata candidate mismatch",
           lambda: (lambda p: ((p / METADATA_NAME).write_text(
                               json.dumps(build_metadata("B")), encoding="utf-8"),
                               rejects(lambda: validate_artifact_directory("A", p))))(make_fixture("A")))
    record("TS-ART-14", "Reject metadata with wrong vocabulary size",
           lambda: (lambda p: ((p / METADATA_NAME).write_text(
                               json.dumps({**build_metadata("A"), "vocab_size": 32000}),
                               encoding="utf-8"),
                               rejects(lambda: validate_artifact_directory("A", p))))(make_fixture("A")))
    record("TS-ART-15", "Reject backend file hash mismatch",
           lambda: (lambda p: ((p / BACKEND_FILES["A"]).write_bytes(b"tampered"),
                               rejects(lambda: validate_artifact_directory("A", p))))(make_fixture("A")))
    record("TS-ART-16", "Reject metadata file hash mismatch",
           lambda: (lambda p: ((p / METADATA_NAME).write_text(
                               json.dumps({**build_metadata("A"), "trainer_note": "tampered"}),
                               encoding="utf-8"),
                               rejects(lambda: validate_artifact_directory("A", p))))(make_fixture("A")))
    record("TS-ART-17", "Reject unsupported artifact schema version",
           lambda: (lambda p: ((lambda m: (m.update(artifact_schema_version="9.0"),
                               (p / MANIFEST_NAME).write_text(json.dumps(m))))(
                                   json.loads((p / MANIFEST_NAME).read_text())),
                               rejects(lambda: validate_artifact_directory("A", p))))(make_fixture("A")))
    record("TS-ART-18", "Reject non-object manifest JSON",
           lambda: (lambda p: ((p / MANIFEST_NAME).write_text("[]", encoding="utf-8"),
                               rejects(lambda: validate_artifact_directory("A", p))))(make_fixture("A")))
    record("TS-ART-19", "Reject unsupported candidate selector",
           lambda: rejects(lambda: validate_artifact_directory("C", a)))
    record("TS-ART-20", "Report layout valid without claiming model loaded",
           lambda: (lambda result: (result["layout_valid"] is True,
                                    result["model_loaded"] is False))(validate_artifact_directory("A", a)))

    return rows


if __name__ == "__main__":
    rows = run_artifact_contract_tests()
    for test_id, name, status, detail in rows:
        print(f"{test_id:14} {status:4} {name}")
        if detail:
            print("   ", detail)
    passed = sum(row[2] == "PASS" for row in rows)
    failed = len(rows) - passed
    print(f"TOTAL: {len(rows)} | PASS: {passed} | FAIL: {failed}")
    raise SystemExit(1 if failed else 0)
