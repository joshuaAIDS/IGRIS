"""
tests/test_phase21b3b_metadata_capacity_and_test_reconciliation.py

Automated verification suite for IGRIS Phase 21B3B:
Final Metadata, Capacity Lifecycle, Test-Suite Reconciliation, and Compute Evidence Audit.
"""

import os
import csv
import hashlib
import pytest

PATCH_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ARTIFACT_DIR = r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102"

EXPECTED_CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
EXPECTED_CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

PINNED_COMMIT_SHA = "984b75b20ce408f9ba27c6558e9279e8e1b6edfd"
TOTAL_UPSTREAM_BYTES = 183700000000  # 183.70 GB


def sha256_file(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_01_all_phase21b3b_deliverables_exist_and_non_empty():
    deliverables = [
        "PHASE21B3B_GIT_BLOB_LFS_POINTER_AUDIT.csv",
        "PHASE21B3B_OBJECT_IDENTITY_EVIDENCE.md",
        "PHASE21B3B_PEAK_STORAGE_CAPACITY_MODEL.csv",
        "PHASE21B3B_STORAGE_LIFECYCLE_ANALYSIS.md",
        "PHASE21B3B_HISTORICAL_TEST_RECONCILIATION.csv",
        "PHASE21B3B_COMPUTE_CLAIM_QUALIFICATION.md",
        "PHASE21B3B_COMPLETION_REPORT.md",
    ]
    for d in deliverables:
        patch_path = os.path.join(PATCH_DIR, d)
        assert os.path.isfile(patch_path), f"Missing in patch dir: {patch_path}"
        assert os.path.getsize(patch_path) > 0, f"Empty in patch dir: {patch_path}"

        artifact_path = os.path.join(ARTIFACT_DIR, d)
        assert os.path.isfile(artifact_path), f"Missing in artifact dir: {artifact_path}"
        assert os.path.getsize(artifact_path) > 0, f"Empty in artifact dir: {artifact_path}"


def test_02_git_blob_lfs_pointer_audit_contents():
    csv_path = os.path.join(PATCH_DIR, "PHASE21B3B_GIT_BLOB_LFS_POINTER_AUDIT.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    assert len(reader) == 9, f"Expected 9 rows in audit CSV, found {len(reader)}"

    total_bytes = 0
    for row in reader:
        assert row["pinned_commit_sha"] == PINNED_COMMIT_SHA
        assert row["git_tree_entry_status"] == "NOT_EXPOSED_IN_TREE_JSON"
        assert row["git_blob_identifier"] == "NOT_EXPOSED_IN_TREE_JSON"
        assert row["lfs_pointer_status"] == "NOT_EXPOSED_WITHOUT_POINTER_INSPECTION"
        assert row["lfs_sha256_oid"] == "NOT_EXPOSED_WITHOUT_POINTER_INSPECTION"
        assert row["content_sha256_status"] == "NOT_VERIFIABLE_WITHOUT_DOWNLOAD"
        assert row["identity_verification_classification"] == "PARTIAL_SIZE_ONLY"
        total_bytes += int(row["lfs_declared_size_bytes"])

    assert total_bytes == TOTAL_UPSTREAM_BYTES, f"Expected {TOTAL_UPSTREAM_BYTES}, got {total_bytes}"


def test_03_zero_hash_fabrication_invariant():
    csv_path = os.path.join(PATCH_DIR, "PHASE21B3B_GIT_BLOB_LFS_POINTER_AUDIT.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    for row in reader:
        blob_id = row["git_blob_identifier"]
        oid = row["lfs_sha256_oid"]
        # Must not be a synthetic 40-char or 64-char hex string
        assert not (len(blob_id) == 40 and all(c in "0123456789abcdef" for c in blob_id.lower())), \
            f"Fabricated Git blob SHA-1 detected: {blob_id}"
        assert not (len(oid) == 64 and all(c in "0123456789abcdef" for c in oid.lower())), \
            f"Fabricated LFS OID detected: {oid}"

    # Verify object identity report explicitly enforces no fabrication
    md_path = os.path.join(PATCH_DIR, "PHASE21B3B_OBJECT_IDENTITY_EVIDENCE.md")
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Zero Hash Fabrication Invariant" in content
    assert "PARTIAL_SIZE_ONLY" in content


def test_04_storage_capacity_three_models_arithmetic():
    csv_path = os.path.join(PATCH_DIR, "PHASE21B3B_PEAK_STORAGE_CAPACITY_MODEL.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = {row["model_id"]: row for row in csv.DictReader(f)}

    assert "MODEL_A" in reader
    assert "MODEL_B" in reader
    assert "MODEL_B_WORST_CASE" in reader
    assert "MODEL_C" in reader

    # Model A: Minimum Theoretical
    assert float(reader["MODEL_A"]["total_capacity_gb_decimal"]) == 421.48
    assert float(reader["MODEL_A"]["total_capacity_gib_binary"]) == 392.53

    # Model B: Peak Simultaneous Operational (Stage 6)
    assert float(reader["MODEL_B"]["total_capacity_gb_decimal"]) == 511.48
    assert float(reader["MODEL_B"]["total_capacity_gib_binary"]) == 476.35

    # Model B Worst-Case: All unpruned buffers
    assert float(reader["MODEL_B_WORST_CASE"]["total_capacity_gb_decimal"]) == 878.88
    assert float(reader["MODEL_B_WORST_CASE"]["total_capacity_gib_binary"]) == 818.52

    # Model C: Long-Term Retained
    assert float(reader["MODEL_C"]["total_capacity_gb_decimal"]) == 441.48
    assert float(reader["MODEL_C"]["total_capacity_gib_binary"]) == 411.16


def test_05_cleaned_corpus_projection_labeling():
    analysis_path = os.path.join(PATCH_DIR, "PHASE21B3B_STORAGE_LIFECYCLE_ANALYSIS.md")
    with open(analysis_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "PROJECTED_UNVALIDATED" in content
    assert "137.78" in content

    completion_path = os.path.join(PATCH_DIR, "PHASE21B3B_COMPLETION_REPORT.md")
    with open(completion_path, "r", encoding="utf-8") as f:
        report_content = f.read()
    assert "PROJECTED_UNVALIDATED" in report_content


def test_06_historical_test_suite_reconciliation():
    csv_path = os.path.join(PATCH_DIR, "PHASE21B3B_HISTORICAL_TEST_RECONCILIATION.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = {r["phase_id"]: r for r in csv.DictReader(f)}

    # Historical full suite baseline at Phase 20A
    assert "PHASE20A" in rows
    assert int(rows["PHASE20A"]["tests_passed"]) == 470
    assert rows["PHASE20A"]["test_type_classification"] == "FULL_SUITE_HISTORICAL"

    # Phase 21B recorded 38 test files
    assert "PHASE21B" in rows
    assert int(rows["PHASE21B"]["number_of_test_files"]) == 38

    # Focused regression group files
    assert int(rows["PHASE20B"]["tests_passed"]) == 4
    assert int(rows["PHASE21"]["tests_passed"]) == 6
    assert int(rows["PHASE21A"]["tests_passed"]) == 4
    assert int(rows["PHASE21B"]["tests_passed"]) == 7
    assert int(rows["PHASE21B1"]["tests_passed"]) == 7
    assert int(rows["PHASE21B2"]["tests_passed"]) == 7
    assert int(rows["PHASE21B3"]["tests_passed"]) == 7
    assert int(rows["PHASE21B3A"]["tests_passed"]) == 8

    # Sum of focused tests from 20B to 21B3A equals exactly 50 tests
    sum_focused = (
        int(rows["PHASE20B"]["tests_passed"]) +
        int(rows["PHASE21"]["tests_passed"]) +
        int(rows["PHASE21A"]["tests_passed"]) +
        int(rows["PHASE21B"]["tests_passed"]) +
        int(rows["PHASE21B1"]["tests_passed"]) +
        int(rows["PHASE21B2"]["tests_passed"]) +
        int(rows["PHASE21B3"]["tests_passed"]) +
        int(rows["PHASE21B3A"]["tests_passed"])
    )
    assert sum_focused == 50, f"Expected 50 focused tests, got {sum_focused}"


def test_07_compute_claim_qualification_and_citations():
    doc_path = os.path.join(PATCH_DIR, "PHASE21B3B_COMPUTE_CLAIM_QUALIFICATION.md")
    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Citations
    assert "Hoffmann et al." in content or "Chinchilla" in content
    assert "Touvron et al." in content or "LLaMA" in content
    assert "Gemma" in content
    assert "LLaMA-3" in content or "Dubey et al." in content

    # Qualified observation
    assert "empirical, non-universal industry observation" in content
    assert "inference-optimization trade-off" in content


def test_08_igris_model_parameter_arithmetic():
    # Model parameters
    untied_params = 96485888
    tied_params = 79708672
    placeholder_params = 73400000

    chinchilla_ratio = 20
    scenario_tokens = 25000000000

    # Untied
    untied_chinchilla_target = untied_params * chinchilla_ratio
    assert untied_chinchilla_target == 1929717760
    untied_tokens_per_param = scenario_tokens / untied_params
    assert round(untied_tokens_per_param, 2) == 259.11
    untied_mult = untied_tokens_per_param / chinchilla_ratio
    assert round(untied_mult, 1) == 13.0

    # Tied
    tied_chinchilla_target = tied_params * chinchilla_ratio
    assert tied_chinchilla_target == 1594173440
    tied_tokens_per_param = scenario_tokens / tied_params
    assert round(tied_tokens_per_param, 2) == 313.64
    tied_mult = tied_tokens_per_param / chinchilla_ratio
    assert round(tied_mult, 1) == 15.7

    # Placeholder
    placeholder_tokens_per_param = scenario_tokens / placeholder_params
    assert round(placeholder_tokens_per_param, 2) == 340.60
    placeholder_mult = placeholder_tokens_per_param / chinchilla_ratio
    assert round(placeholder_mult, 1) == 17.0


def test_09_tokenizer_physical_hashes_invariant():
    cand_a_path = os.path.join(PATCH_DIR, "artifacts", "tokenizer", "candidate_a", "tokenizer.json")
    cand_b_path = os.path.join(PATCH_DIR, "artifacts", "tokenizer", "candidate_b", "tokenizer.model")

    assert os.path.isfile(cand_a_path), f"Candidate A missing: {cand_a_path}"
    assert os.path.isfile(cand_b_path), f"Candidate B missing: {cand_b_path}"

    hash_a = sha256_file(cand_a_path)
    hash_b = sha256_file(cand_b_path)

    assert hash_a == EXPECTED_CANDIDATE_A_HASH, f"Candidate A hash mismatch: {hash_a}"
    assert hash_b == EXPECTED_CANDIDATE_B_HASH, f"Candidate B hash mismatch: {hash_b}"


def test_10_governance_invariants_preserved():
    # Check Completion Report
    report_path = os.path.join(PATCH_DIR, "PHASE21B3B_COMPLETION_REPORT.md")
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "VERDICT A — ALL METADATA, STORAGE LIFECYCLE, HISTORICAL TEST RECORDS AND COMPUTE ARITHMETIC RECONCILED" in content
    assert "SOLO_DEVELOPER_OWNER_REVIEW" in content
    assert "LOCKED" in content
    assert "Mandatory Stop Condition" in content
