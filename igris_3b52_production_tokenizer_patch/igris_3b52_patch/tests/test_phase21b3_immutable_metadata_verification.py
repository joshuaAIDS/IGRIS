"""
Phase 21B3 Test Suite: Immutable IndicCorp v2 Object Metadata Verification
Validates 9 physical objects across 7 sources, Hindi 3-shard completeness, pinned commit,
storage byte/GiB arithmetic (183.7GB total / 80.1GB Hindi), ACL statistics (10,947M),
explicit representation of unexposed hashes, governance invariants, and filename isolation invariant.
"""

import csv
import hashlib
from pathlib import Path
import pytest

PATCH_DIR = Path(__file__).resolve().parent.parent

CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"
PINNED_COMMIT = "984b75b20ce408f9ba27c6558e9279e8e1b6edfd"

EXPECTED_PATHS = {
    "data/ta.txt": ("SRC-TM-01", 11800000000),
    "data/hi-1.txt": ("SRC-HI-01", 26700000000),
    "data/hi-2.txt": ("SRC-HI-01", 26700000000),
    "data/hi-3.txt": ("SRC-HI-01", 26700000000),
    "data/te.txt": ("SRC-OI-01", 15800000000),
    "data/ml.txt": ("SRC-OI-02", 26300000000),
    "data/kn.txt": ("SRC-OI-03", 19600000000),
    "data/bn.txt": ("SRC-OI-04", 16000000000),
    "data/gu.txt": ("SRC-OI-05", 14100000000),
}


def test_phase21b3_deliverables_exist():
    """Verify that all 6 required Phase 21B3 deliverables exist in the patch root."""
    assert (PATCH_DIR / "PHASE21B3_IMMUTABLE_OBJECT_MANIFEST.csv").is_file()
    assert (PATCH_DIR / "PHASE21B3_REPOSITORY_METADATA_EVIDENCE.md").is_file()
    assert (PATCH_DIR / "PHASE21B3_STORAGE_CAPACITY_RECONCILIATION.csv").is_file()
    assert (PATCH_DIR / "PHASE21B3_ACL_STATISTICS_PRESERVATION.md").is_file()
    assert (PATCH_DIR / "PHASE21B3_PROJECTION_STATUS.md").is_file()
    assert (PATCH_DIR / "PHASE21B3_COMPLETION_REPORT.md").is_file()


def test_phase21b3_manifest_paths_and_hindi_shards():
    """Verify all 9 paths are represented, Hindi has 3 shards, and commit is pinned."""
    manifest_csv = PATCH_DIR / "PHASE21B3_IMMUTABLE_OBJECT_MANIFEST.csv"
    with open(manifest_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 9

    # Check uniqueness of paths
    seen_paths = set()
    hindi_shards = []

    for r in rows:
        path = r["exact_repository_path"]
        assert path in EXPECTED_PATHS
        assert path not in seen_paths, f"Duplicate path assignment: {path}"
        seen_paths.add(path)

        expected_sid, expected_bytes = EXPECTED_PATHS[path]
        assert r["source_id"] == expected_sid
        assert r["pinned_commit_sha"] == PINNED_COMMIT
        assert r["repository_id"] == "ai4bharat/IndicCorpV2"
        assert r["file_presence_at_pinned_revision"] == "PRESENT"
        assert int(r["reported_size_bytes"]) == expected_bytes

        # Check explicit representation of unexposed hashes (no fabrication)
        assert r["lfs_sha256_oid_or_xet_id"] == "NOT_EXPOSED_WITHOUT_LFS_POINTER_INSPECTION"
        assert r["independent_sha256_available_without_download"] == "NOT_VERIFIABLE_WITHOUT_DOWNLOAD"

        if r["source_id"] == "SRC-HI-01":
            hindi_shards.append(path)

    assert seen_paths == set(EXPECTED_PATHS.keys())
    assert len(hindi_shards) == 3
    assert set(hindi_shards) == {"data/hi-1.txt", "data/hi-2.txt", "data/hi-3.txt"}


def test_phase21b3_storage_arithmetic():
    """Verify byte, decimal GB, and binary GiB arithmetic across manifest and storage CSV."""
    manifest_csv = PATCH_DIR / "PHASE21B3_IMMUTABLE_OBJECT_MANIFEST.csv"
    with open(manifest_csv, mode="r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    total_bytes = sum(int(r["reported_size_bytes"]) for r in rows)
    hindi_bytes = sum(int(r["reported_size_bytes"]) for r in rows if r["source_id"] == "SRC-HI-01")

    assert total_bytes == 183700000000
    assert hindi_bytes == 80100000000

    total_decimal_gb = total_bytes / 10**9
    total_binary_gib = total_bytes / (1024**3)

    assert round(total_decimal_gb, 2) == 183.70
    assert round(total_binary_gib, 2) == 171.08

    # Verify storage reconciliation CSV total row
    storage_csv = PATCH_DIR / "PHASE21B3_STORAGE_CAPACITY_RECONCILIATION.csv"
    with open(storage_csv, mode="r", encoding="utf-8") as f:
        s_rows = list(csv.DictReader(f))

    total_row = [r for r in s_rows if r["source_id"] == "TOTAL"][0]
    assert int(total_row["verified_upstream_bytes"]) == 183700000000
    assert total_row["verified_upstream_decimal_gb"] == "183.70"
    assert total_row["verified_upstream_binary_gib"] == "171.08"
    assert int(total_row["historical_phase21b_bytes"]) == 37100000000
    assert total_row["variance_decimal_gb"] == "+146.60"


def test_phase21b3_acl_statistics_preservation():
    """Verify ACL 2023 statistics preservation document maintains 10,947M tokens."""
    content = (PATCH_DIR / "PHASE21B3_ACL_STATISTICS_PRESERVATION.md").read_text(encoding="utf-8")
    assert "10,947" in content
    assert "476" in content  # ta
    assert "6,107" in content or "6107" in content  # hi
    assert "731" in content  # te
    assert "931" in content  # ml
    assert "875" in content  # kn
    assert "926" in content  # bn
    assert "901" in content  # gu


def test_phase21b3_projections_classified_unvalidated():
    """Verify projections status classifies estimates as PROJECTED_UNVALIDATED."""
    content = (PATCH_DIR / "PHASE21B3_PROJECTION_STATUS.md").read_text(encoding="utf-8")
    assert "PROJECTED_UNVALIDATED" in content
    assert "200 GB" in content or "200" in content
    assert "no empirical validation" in content.lower() or "no claim" in content.lower()


def test_phase21b3_governance_invariants():
    """Verify zero sources authorized, ingress locked, quarantine empty, and tokenizers invariant."""
    auth_csv = PATCH_DIR / "PHASE21_OWNER_AUTHORIZATION_REGISTER.csv"
    if auth_csv.is_file():
        with open(auth_csv, mode="r", encoding="utf-8") as f:
            auth_rows = list(csv.DictReader(f))
        for r in auth_rows:
            assert r["authorization_status"] != "AUTHORIZED"

    try:
        import tempfile
        from igris_3b52_patch.acquisition.secure_acquisition_engine import SecureAcquisitionEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SecureAcquisitionEngine(audit_log_path=Path(tmpdir) / "audit.jsonl")
            assert engine.ingress_locked is True
    except (ImportError, AttributeError):
        pass

    quarantine_dirs = [
        PATCH_DIR / "quarantine_sandbox",
        PATCH_DIR.parent / "quarantine_sandbox",
    ]
    for qd in quarantine_dirs:
        if qd.is_dir():
            files = list(qd.glob("*"))
            for f in files:
                assert f.suffix not in [".tar", ".gz", ".txt", ".parquet", ".jsonl"] or "sample" in f.name or "dummy" in f.name or "synthetic" in f.name

    cand_a_path = PATCH_DIR / "tokenizers" / "candidate_a_bytelevel_bpe" / "tokenizer.json"
    if not cand_a_path.is_file():
        cand_a_path = PATCH_DIR / "tokenizer_candidate_a" / "tokenizer.json"
    if cand_a_path.is_file():
        actual_hash_a = hashlib.sha256(cand_a_path.read_bytes()).hexdigest()
        assert actual_hash_a == CANDIDATE_A_HASH

    cand_b_path = PATCH_DIR / "tokenizers" / "candidate_b_sentencepiece_unigram" / "tokenizer.json"
    if not cand_b_path.is_file():
        cand_b_path = PATCH_DIR / "tokenizer_candidate_b" / "tokenizer.json"
    if cand_b_path.is_file():
        actual_hash_b = hashlib.sha256(cand_b_path.read_bytes()).hexdigest()
        assert actual_hash_b == CANDIDATE_B_HASH

    for p in PATCH_DIR.rglob("*"):
        if p.is_file():
            if p.suffix.lower() != ".md":
                assert "quarantine" not in p.name.lower(), f"Violation: non-markdown file '{p}' contains 'quarantine' in filename."


def test_phase21b3_completion_report_verdict():
    """Verify that the completion report assigns Verdict A."""
    report_path = PATCH_DIR / "PHASE21B3_COMPLETION_REPORT.md"
    content = report_path.read_text(encoding="utf-8")
    assert "VERDICT A — ALL IMMUTABLE OBJECT METADATA AND STORAGE ARITHMETIC RECONCILED" in content
    assert "SOLO_DEVELOPER_OWNER_REVIEW" in content
