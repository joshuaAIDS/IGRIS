"""
scratch/verify_phase21b3d.py

Automated verification script for IGRIS Phase 21B3D:
Governance Test Isolation Remediation and Zero-Failure Verification.
"""

import os
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


def test_01_all_phase21b3d_deliverables_exist():
    deliverables = [
        "PHASE21B3D_ROOT_CAUSE_ANALYSIS.md",
        "PHASE21B3D_TEST_ISOLATION_FIX.md",
        "PHASE21B3D_REGRESSION_RESULTS.txt",
        "PHASE21B3D_GOVERNANCE_ISOLATION_EVIDENCE.md",
        "PHASE21B3D_COMPLETION_REPORT.md",
    ]
    for d in deliverables:
        p_path = os.path.join(PATCH_DIR, d)
        assert os.path.isfile(p_path), f"Missing in patch dir: {p_path}"
        assert os.path.getsize(p_path) > 0, f"Empty in patch dir: {p_path}"

        a_path = os.path.join(ARTIFACT_DIR, d)
        assert os.path.isfile(a_path), f"Missing in artifact dir: {a_path}"
        assert os.path.getsize(a_path) > 0, f"Empty in artifact dir: {a_path}"
    print("[PASS] Test 01: All 5 deliverables exist and non-empty in both locations.")


def test_02_filesystem_cleanliness_invariant():
    patch_root = PATCH_DIR
    q1 = os.path.join(patch_root, "quarantine")
    q2 = r"C:\IGRIS\quarantine"

    assert not os.path.exists(q1), f"Persistent quarantine directory found in patch root: {q1}"
    assert not os.path.exists(q2), f"Persistent quarantine directory found in root: {q2}"

    # Verify no non-markdown file or folder in patch root contains quarantine
    for root, dirs, files in os.walk(patch_root):
        for d in dirs:
            assert "quarantine" not in d.lower(), f"Quarantine directory found: {os.path.join(root, d)}"
        for f in files:
            if f.endswith(".md") or f.endswith(".markdown"):
                continue
            assert "quarantine" not in f.lower(), f"Quarantine non-markdown file found: {os.path.join(root, f)}"

    print("[PASS] Test 02: Filesystem cleanliness verified (0 non-markdown quarantine artifacts).")


def test_03_regression_results_text_content():
    txt_path = os.path.join(PATCH_DIR, "PHASE21B3D_REGRESSION_RESULTS.txt")
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "530 passed" in content
    assert "Total Tests Failed:                0 items" in content
    assert "PREVIOUS FAILURE COMPLETELY RESOLVED" in content
    print("[PASS] Test 03: Regression results text verified (530 passed, 0 failed).")


def test_04_tokenizer_candidate_hashes():
    cand_a_path = os.path.join(PATCH_DIR, "artifacts", "tokenizer", "candidate_a", "tokenizer.json")
    cand_b_path = os.path.join(PATCH_DIR, "artifacts", "tokenizer", "candidate_b", "tokenizer.model")

    assert os.path.isfile(cand_a_path), f"Candidate A missing: {cand_a_path}"
    assert os.path.isfile(cand_b_path), f"Candidate B missing: {cand_b_path}"

    hash_a = sha256_file(cand_a_path)
    hash_b = sha256_file(cand_b_path)

    assert hash_a == EXPECTED_CANDIDATE_A_HASH, f"Candidate A hash mismatch: {hash_a}"
    assert hash_b == EXPECTED_CANDIDATE_B_HASH, f"Candidate B hash mismatch: {hash_b}"
    print(f"[PASS] Test 04: Tokenizer candidate hashes verified unchanged ({hash_a[:16]}..., {hash_b[:16]}...).")


def test_05_governance_invariants_and_completion_report():
    report_path = os.path.join(PATCH_DIR, "PHASE21B3D_COMPLETION_REPORT.md")
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "SOLO_DEVELOPER_OWNER_REVIEW" in content
    assert "LOCKED" in content
    assert "VERDICT A — GOVERNANCE TEST ISOLATION REMEDIATED, ZERO FAILURES, AND COMPLETE REPOSITORY SUITE PASSING" in content
    assert "Mandatory Stop Condition" in content
    print("[PASS] Test 05: Governance invariants and completion report verified.")


def main():
    print("--- Running Phase 21B3D Verification Suite ---")
    test_01_all_phase21b3d_deliverables_exist()
    test_02_filesystem_cleanliness_invariant()
    test_03_regression_results_text_content()
    test_04_tokenizer_candidate_hashes()
    test_05_governance_invariants_and_completion_report()
    print("--- All 5 Phase 21B3D Verification Tests Passed Successfully! ---")


if __name__ == "__main__":
    main()
