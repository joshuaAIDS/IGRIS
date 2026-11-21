# verify_phase23.py
"""
Deterministic independent verification script for Phase 23:
1. Verifies existence and non-emptiness of all 9 Phase 23 deliverables.
2. Validates PHASE23_SOURCE_REVIEW_REGISTER.csv (all 32 sources partitioned).
3. Verifies language categorization (Tamil: 3, English: 11, Tanglish: 3, Out of Scope: 15).
4. Verifies status categorization (Eligible: 6, Pending Legal: 8, Rejected: 3, Out of Scope: 15, Approved: 0).
5. Validates PHASE23_UNRESOLVED_RIGHTS_REGISTER.csv (8 pending legal review sources tracked).
6. Verifies Candidate A and Candidate B cryptographic SHA-256 hashes.
7. Checks that zero production bytes exist in quarantine.
8. Runs readiness and planning pytest suites.
"""

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")
PYTHON_EXE = Path(r"C:\IGRIS\.venv\Scripts\python.exe")

EXPECTED_DELIVERABLES = [
    "PHASE23_LANGUAGE_SCOPE_POLICY.md",
    "PHASE23_SOURCE_REVIEW_REGISTER.csv",
    "PHASE23_TAMIL_SOURCE_LEGAL_REVIEW.md",
    "PHASE23_ENGLISH_SOURCE_LEGAL_REVIEW.md",
    "PHASE23_TANGLISH_SOURCE_LEGAL_REVIEW.md",
    "PHASE23_UNRESOLVED_RIGHTS_REGISTER.csv",
    "PHASE23_OWNER_DECISION_PACKAGE.md",
    "PHASE23_COMPLETION_REPORT.md",
    "verify_phase23.py",
]

EXPECTED_CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
EXPECTED_CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def test_deliverables_exist():
    print("1. Checking Phase 23 deliverables exist and non-empty...")
    for d in EXPECTED_DELIVERABLES:
        p_patch = PATCH_ROOT / d
        p_art = ARTIFACT_DIR / d
        assert p_patch.exists(), f"Missing in patch root: {p_patch}"
        assert p_patch.stat().st_size > 0, f"Empty file in patch root: {p_patch}"
        assert p_art.exists(), f"Missing in artifact dir: {p_art}"
        assert p_art.stat().st_size > 0, f"Empty file in artifact dir: {p_art}"
        print(f"  [OK] {d} (Patch: {p_patch.stat().st_size} bytes, Artifact: {p_art.stat().st_size} bytes)")

def test_source_review_register():
    print("\n2. Verifying 32-source review register partitioning...")
    csv_path = PATCH_ROOT / "PHASE23_SOURCE_REVIEW_REGISTER.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 32, f"Expected 32 sources, got {len(rows)}"

    # Language breakdown
    tamil_sources = [r for r in rows if r["language_category"] == "TAMIL"]
    english_sources = [r for r in rows if r["language_category"] == "ENGLISH"]
    tanglish_sources = [r for r in rows if r["language_category"] == "TANGLISH"]
    out_of_scope_sources = [r for r in rows if r["language_category"] == "OUT_OF_SCOPE"]

    assert len(tamil_sources) == 3, f"Expected 3 Tamil sources, got {len(tamil_sources)}"
    assert len(english_sources) == 11, f"Expected 11 English sources, got {len(english_sources)}"
    assert len(tanglish_sources) == 3, f"Expected 3 Tanglish sources, got {len(tanglish_sources)}"
    assert len(out_of_scope_sources) == 15, f"Expected 15 Out of Scope sources, got {len(out_of_scope_sources)}"

    # Status breakdown
    eligible = [r for r in rows if r["owner_decision_status"] == "ELIGIBLE_FOR_OWNER_REVIEW"]
    pending_legal = [r for r in rows if r["owner_decision_status"] == "PENDING_OWNER_AUTHORIZATION" and r["legal_review_status"] == "PENDING_LEGAL_REVIEW"]
    rejected = [r for r in rows if r["owner_decision_status"] == "REJECTED"]
    out_scope_status = [r for r in rows if r["owner_decision_status"] == "OUT_OF_SCOPE"]
    approved = [r for r in rows if r["owner_decision_status"] == "APPROVED_FOR_CONTROLLED_ACQUISITION"]

    assert len(eligible) == 6, f"Expected 6 eligible sources, got {len(eligible)}"
    assert len(pending_legal) == 8, f"Expected 8 pending legal sources, got {len(pending_legal)}"
    assert len(rejected) == 3, f"Expected 3 rejected sources, got {len(rejected)}"
    assert len(out_scope_status) == 15, f"Expected 15 out of scope sources, got {len(out_scope_status)}"
    assert len(approved) == 0, f"Zero sources must be approved, got {len(approved)}"

    print(f"  [OK] Language scope verified: Tamil={len(tamil_sources)}, English={len(english_sources)}, Tanglish={len(tanglish_sources)}, OutOfScope={len(out_of_scope_sources)} (Total=32).")
    print(f"  [OK] Status breakdown verified: Eligible={len(eligible)}, PendingLegal={len(pending_legal)}, Rejected={len(rejected)}, OutOfScope={len(out_scope_status)}, Approved={len(approved)}.")

def test_unresolved_rights_register():
    print("\n3. Verifying unresolved rights register...")
    csv_path = PATCH_ROOT / "PHASE23_UNRESOLVED_RIGHTS_REGISTER.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 8, f"Expected 8 pending legal sources in unresolved rights register, got {len(rows)}"
    for r in rows:
        assert r["blocking_status"] == "BLOCKING_ACQUISITION", f"Source {r['source_id']} must have BLOCKING_ACQUISITION status"
    print(f"  [OK] All {len(rows)} legal risks cataloged with BLOCKING_ACQUISITION status.")

def test_governance_and_tokenizers():
    print("\n4. Verifying tokenizer cryptographic hashes and governance locks...")
    cand_a_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    cand_b_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"

    hash_a = compute_sha256(cand_a_path)
    hash_b = compute_sha256(cand_b_path)

    assert hash_a == EXPECTED_CANDIDATE_A_HASH, f"Candidate A hash mismatch: {hash_a}"
    assert hash_b == EXPECTED_CANDIDATE_B_HASH, f"Candidate B hash mismatch: {hash_b}"
    print(f"  [OK] Candidate A SHA-256 verified: {hash_a}")
    print(f"  [OK] Candidate B SHA-256 verified: {hash_b}")

    quarantine_raw = PATCH_ROOT / "quarantine" / "raw"
    if quarantine_raw.exists():
        files = list(quarantine_raw.glob("*"))
        assert len(files) == 0, f"Found files in quarantine raw: {files}"
    print("  [OK] Zero production data files in quarantine.")

def test_readiness_pytest_suites():
    print("\n5. Running pytest readiness and planning suites...")
    res1 = subprocess.run([str(PYTHON_EXE), "-m", "pytest", str(PATCH_ROOT / "tests" / "test_readiness.py"), "-q"], cwd=str(PATCH_ROOT), capture_output=True, text=True)
    assert res1.returncode == 0 and "5 passed" in res1.stdout, f"test_readiness failed: {res1.stdout}\n{res1.stderr}"
    print("  [OK] test_readiness.py passed (5/5)")

    res2 = subprocess.run([str(PYTHON_EXE), "-m", "pytest", str(PATCH_ROOT / "tests" / "test_phase22_production_planning.py"), "-q"], cwd=str(PATCH_ROOT), capture_output=True, text=True)
    assert res2.returncode == 0 and "6 passed" in res2.stdout, f"test_phase22_production_planning failed: {res2.stdout}\n{res2.stderr}"
    print("  [OK] test_phase22_production_planning.py passed (6/6)")

def main():
    print("==================================================================")
    print("  IGRIS PHASE 23 DETERMINISTIC VERIFICATION SUITE")
    print("==================================================================")
    test_deliverables_exist()
    test_source_review_register()
    test_unresolved_rights_register()
    test_governance_and_tokenizers()
    test_readiness_pytest_suites()
    print("\n==================================================================")
    print("  ALL PHASE 23 VERIFICATION CHECKS PASSED PERFECTLY (100%)")
    print("==================================================================")

if __name__ == "__main__":
    main()
