"""
scratch/verify_phase21b3c.py

Automated verification script for IGRIS Phase 21B3C deliverables and governance invariants.
"""

import os
import csv
import hashlib

PATCH_DIR = r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch"
ARTIFACT_DIR = r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102"

EXPECTED_CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
EXPECTED_CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"


def sha256_file(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_01_all_phase21b3c_deliverables_exist_and_non_empty():
    deliverables = [
        "PHASE21B3C_TEST_INVENTORY.csv",
        "PHASE21B3C_PYTEST_COLLECTION_OUTPUT.txt",
        "PHASE21B3C_TEST_COUNT_RECONCILIATION.md",
        "PHASE21B3C_OBJECT_IDENTITY_STATUS.csv",
        "PHASE21B3C_OBJECT_IDENTITY_LIMITATIONS.md",
        "PHASE21B3C_VERDICT_CORRECTION.md",
        "PHASE21B3C_COMPLETION_REPORT.md",
    ]
    for d in deliverables:
        p_path = os.path.join(PATCH_DIR, d)
        assert os.path.isfile(p_path), f"Missing in patch dir: {p_path}"
        assert os.path.getsize(p_path) > 0, f"Empty in patch dir: {p_path}"

        a_path = os.path.join(ARTIFACT_DIR, d)
        assert os.path.isfile(a_path), f"Missing in artifact dir: {a_path}"
        assert os.path.getsize(a_path) > 0, f"Empty in artifact dir: {a_path}"
    print("[PASS] Test 01: All 7 deliverables exist and non-empty in both locations.")


def test_02_test_inventory_csv_structure_and_counts():
    csv_path = os.path.join(PATCH_DIR, "PHASE21B3C_TEST_INVENTORY.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 43, f"Expected 43 rows, found {len(rows)}"

    hist_rows = [r for r in rows if r["baseline_classification"] == "HISTORICAL_BASELINE"]
    foc_rows = [r for r in rows if r["baseline_classification"] == "FOCUSED_PHASE_EXTENSION"]

    assert len(hist_rows) == 34, f"Expected 34 historical files, found {len(hist_rows)}"
    assert len(foc_rows) == 9, f"Expected 9 focused files, found {len(foc_rows)}"

    hist_cases = sum(int(r["collected_test_cases"]) for r in hist_rows)
    foc_cases = sum(int(r["collected_test_cases"]) for r in foc_rows)

    assert hist_cases == 470, f"Expected 470 historical cases, got {hist_cases}"
    assert foc_cases == 60, f"Expected 60 focused cases, got {foc_cases}"
    assert hist_cases + foc_cases == 530, f"Expected 530 total cases, got {hist_cases + foc_cases}"

    print(f"[PASS] Test 02: Test inventory CSV verified: 43 files (34 historical = 470 cases; 9 focused = 60 cases; Total = 530).")


def test_03_pytest_collection_output_content():
    txt_path = os.path.join(PATCH_DIR, "PHASE21B3C_PYTEST_COLLECTION_OUTPUT.txt")
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "530 tests collected" in content
    print("[PASS] Test 03: Pytest collection output contains '530 tests collected'.")


def test_04_object_identity_status_csv():
    csv_path = os.path.join(PATCH_DIR, "PHASE21B3C_OBJECT_IDENTITY_STATUS.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 9, f"Expected 9 rows, got {len(rows)}"
    total_bytes = 0
    for r in rows:
        assert r["pinned_commit_sha"] == "984b75b20ce408f9ba27c6558e9279e8e1b6edfd"
        assert r["git_tree_entry_id"] == "NOT_EXPOSED_IN_TREE_JSON"
        assert r["git_blob_sha1"] == "NOT_EXPOSED_IN_TREE_JSON"
        assert r["lfs_pointer_sha256_oid"] == "NOT_EXPOSED_WITHOUT_POINTER_OR_DOWNLOAD"
        assert r["downloaded_payload_sha256"] == "NOT_VERIFIABLE_WITHOUT_DOWNLOAD"
        assert r["evidence_accessibility_status"] == "EVIDENCE_PARTIALLY_AVAILABLE"
        assert r["identity_verification_classification"] == "METADATA_ACCESSIBLE_PAYLOAD_UNINSPECTED"
        total_bytes += int(r["declared_size_bytes"])

    assert total_bytes == 183700000000, f"Expected 183700000000 bytes, got {total_bytes}"
    print(f"[PASS] Test 04: Object identity CSV verified (9 files, 183,700,000,000 bytes, unexposed hash statuses, zero fabrication).")


def test_05_object_identity_limitations_md():
    md_path = os.path.join(PATCH_DIR, "PHASE21B3C_OBJECT_IDENTITY_LIMITATIONS.md")
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "PARTIAL_SIZE_ONLY" in content
    assert "METADATA_ACCESSIBLE_PAYLOAD_UNINSPECTED" in content
    assert "Zero Hash Fabrication" in content or "Proscription Against Hash Fabrication" in content
    print("[PASS] Test 05: Object identity limitations report verified.")


def test_06_test_count_reconciliation_md():
    md_path = os.path.join(PATCH_DIR, "PHASE21B3C_TEST_COUNT_RECONCILIATION.md")
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "470" in content
    assert "34" in content
    assert "38" in content
    assert "43" in content
    assert "60" in content
    assert "530" in content
    assert "529 passed" in content
    assert "1 failed" in content
    assert "test_governance_isolation_check" in content
    assert "quarantine" in content
    print("[PASS] Test 06: Test count reconciliation report verified (reconciles 470, 34, 38, 43, 60, 530, 529 passed / 1 failed).")


def test_07_verdict_correction_md():
    md_path = os.path.join(PATCH_DIR, "PHASE21B3C_VERDICT_CORRECTION.md")
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Must contain the four standardized precision phrases
    assert "Evidence available and verified" in content
    assert "Evidence partially available" in content
    assert "Evidence unavailable without authorized acquisition" in content
    assert "Historical claim not independently reproducible" in content
    print("[PASS] Test 07: Verdict correction report verified with all 4 standardized precision phrases.")


def test_08_tokenizer_physical_hashes():
    cand_a_path = os.path.join(PATCH_DIR, "artifacts", "tokenizer", "candidate_a", "tokenizer.json")
    cand_b_path = os.path.join(PATCH_DIR, "artifacts", "tokenizer", "candidate_b", "tokenizer.model")

    assert os.path.isfile(cand_a_path), f"Candidate A missing: {cand_a_path}"
    assert os.path.isfile(cand_b_path), f"Candidate B missing: {cand_b_path}"

    hash_a = sha256_file(cand_a_path)
    hash_b = sha256_file(cand_b_path)

    assert hash_a == EXPECTED_CANDIDATE_A_HASH, f"Candidate A hash mismatch: {hash_a}"
    assert hash_b == EXPECTED_CANDIDATE_B_HASH, f"Candidate B hash mismatch: {hash_b}"
    print(f"[PASS] Test 08: Tokenizer candidate hashes verified unchanged ({hash_a[:16]}..., {hash_b[:16]}...).")


def test_09_governance_invariants():
    report_path = os.path.join(PATCH_DIR, "PHASE21B3C_COMPLETION_REPORT.md")
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "SOLO_DEVELOPER_OWNER_REVIEW" in content
    assert "LOCKED" in content
    assert "VERDICT A — CURRENT TEST INVENTORY REPRODUCIBLY RECONCILED" in content
    assert "Mandatory Stop Condition" in content
    print("[PASS] Test 09: Governance invariants and completion report verified.")


def main():
    print("--- Running Phase 21B3C Verification Suite ---")
    test_01_all_phase21b3c_deliverables_exist_and_non_empty()
    test_02_test_inventory_csv_structure_and_counts()
    test_03_pytest_collection_output_content()
    test_04_object_identity_status_csv()
    test_05_object_identity_limitations_md()
    test_06_test_count_reconciliation_md()
    test_07_verdict_correction_md()
    test_08_tokenizer_physical_hashes()
    test_09_governance_invariants()
    print("--- All 9 Phase 21B3C Verification Tests Passed Successfully! ---")


if __name__ == "__main__":
    main()
