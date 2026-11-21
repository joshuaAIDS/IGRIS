# verify_phase23b.py
"""
Deterministic independent verification script for Phase 23B:
1. Verifies existence and non-emptiness of all 8 Phase 23B deliverables.
2. Validates PHASE23B_SOURCE_ID_CORRECTION_REGISTER.csv (SRC-CV-06 & SRC-CV-07 reconciliation).
3. Validates PHASE23B_ENGLISH_SOURCE_RECONCILIATION.csv (7 distinct candidates, 6 verified for review, 1 pending legal).
4. Validates PHASE23B_TANGLISH_LINGUISTIC_EVALUATION.csv (100 itemized evaluations, valid 1-5 scores).
5. Verifies Candidate A and Candidate B cryptographic SHA-256 hashes.
6. Verifies zero production bytes in quarantine raw directory.
7. Executes pytest readiness and production planning test suites.
"""

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")
PYTHON_EXE = Path(r"C:\IGRIS\.venv\Scripts\python.exe")

EXPECTED_DELIVERABLES = [
    "PHASE23B_SOURCE_IDENTITY_AUDIT.md",
    "PHASE23B_SOURCE_ID_CORRECTION_REGISTER.csv",
    "PHASE23B_ENGLISH_SOURCE_RECONCILIATION.csv",
    "PHASE23B_TANGLISH_LINGUISTIC_EVALUATION.csv",
    "PHASE23B_TANGLISH_QUALITY_ANALYSIS.md",
    "PHASE23B_GENERATOR_IMPROVEMENTS.md",
    "PHASE23B_COMPLETION_REPORT.md",
    "verify_phase23b.py",
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
    print("1. Checking Phase 23B deliverables exist and non-empty...")
    for d in EXPECTED_DELIVERABLES:
        p_patch = PATCH_ROOT / d
        p_art = ARTIFACT_DIR / d
        assert p_patch.exists(), f"Missing in patch root: {p_patch}"
        assert p_patch.stat().st_size > 0, f"Empty file in patch root: {p_patch}"
        assert p_art.exists(), f"Missing in artifact dir: {p_art}"
        assert p_art.stat().st_size > 0, f"Empty file in artifact dir: {p_art}"
        print(f"  [OK] {d} (Patch: {p_patch.stat().st_size} bytes, Artifact: {p_art.stat().st_size} bytes)")

def test_source_id_correction_register():
    print("\n2. Validating Source ID Correction Register...")
    csv_path = PATCH_ROOT / "PHASE23B_SOURCE_ID_CORRECTION_REGISTER.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) >= 1, "Correction register must contain at least 1 record"
    rec = rows[0]
    assert rec["permanent_source_id_dataset_1"] == "SRC-CV-06"
    assert "Gutenberg Theatrical" in rec["dataset_1_reaffirmed_identity"]
    assert rec["permanent_source_id_dataset_2"] == "SRC-CV-07"
    assert "WikiDialog" in rec["dataset_2_reassigned_identity"]
    assert rec["correction_status"] == "RECONCILED_AND_CODIFIED"
    print("  [OK] SRC-CV-06 reaffirmed as Gutenberg Theatrical; SRC-CV-07 codified as WikiDialog English.")

def test_english_source_reconciliation():
    print("\n3. Validating English Source Reconciliation Register...")
    csv_path = PATCH_ROOT / "PHASE23B_ENGLISH_SOURCE_RECONCILIATION.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 7, f"Expected 7 distinct English candidate sources, got {len(rows)}"
    expected_ids = {"SRC-EN-01", "SRC-TD-02", "SRC-TD-03", "SRC-CV-03", "SRC-CV-05", "SRC-CV-06", "SRC-CV-07"}
    actual_ids = {r["source_id"] for r in rows}
    assert actual_ids == expected_ids, f"ID set mismatch: {actual_ids} vs {expected_ids}"

    verified = [r for r in rows if r["classification_status"] == "VERIFIED_FOR_OWNER_REVIEW"]
    pending = [r for r in rows if r["classification_status"] == "PENDING_LEGAL_REVIEW"]

    assert len(verified) == 6, f"Expected 6 verified for owner review, got {len(verified)}"
    assert len(pending) == 1, f"Expected 1 pending legal review, got {len(pending)}"
    assert pending[0]["source_id"] == "SRC-CV-07"
    print(f"  [OK] 7 distinct English sources validated: 6 Verified for Owner Review, 1 Pending Legal Review (SRC-CV-07).")

def test_tanglish_linguistic_evaluation():
    print("\n4. Validating Tanglish Linguistic Evaluation...")
    csv_path = PATCH_ROOT / "PHASE23B_TANGLISH_LINGUISTIC_EVALUATION.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 100, f"Expected 100 evaluated fixtures, got {len(rows)}"

    scores = []
    for r in rows:
        comp = float(r["composite_score"])
        assert 1.0 <= comp <= 5.0, f"Invalid composite score {comp} in {r['fixture_id']}"
        scores.append(comp)

        # Check individual dimensions
        for dim in ["tamil_comprehensibility", "english_naturalness", "structural_plausibility", "romanization_readability", "grammatical_acceptability", "conversational_fluency"]:
            val = int(r[dim])
            assert 1 <= val <= 5, f"Invalid dimension value {val} for {dim} in {r['fixture_id']}"

    mean_score = sum(scores) / len(scores)
    assert 4.0 <= mean_score <= 4.5, f"Mean score outside expected range: {mean_score}"
    print(f"  [OK] 100 fixtures evaluated across 6 dimensions. Mean score: {mean_score:.2f} / 5.0.")

def test_governance_and_tokenizers():
    print("\n5. Verifying tokenizer cryptographic hashes and governance locks...")
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

def test_pytest_suites():
    print("\n6. Running pytest readiness and production planning test suites...")
    res1 = subprocess.run([str(PYTHON_EXE), "-m", "pytest", str(PATCH_ROOT / "tests" / "test_readiness.py"), "-q"], cwd=str(PATCH_ROOT), capture_output=True, text=True)
    assert res1.returncode == 0 and "5 passed" in res1.stdout, f"test_readiness failed: {res1.stdout}\n{res1.stderr}"
    print("  [OK] test_readiness.py passed (5/5)")

    res2 = subprocess.run([str(PYTHON_EXE), "-m", "pytest", str(PATCH_ROOT / "tests" / "test_phase22_production_planning.py"), "-q"], cwd=str(PATCH_ROOT), capture_output=True, text=True)
    assert res2.returncode == 0 and "6 passed" in res2.stdout, f"test_phase22_production_planning failed: {res2.stdout}\n{res2.stderr}"
    print("  [OK] test_phase22_production_planning.py passed (6/6)")

def main():
    print("==================================================================")
    print("  IGRIS PHASE 23B DETERMINISTIC VERIFICATION SUITE")
    print("==================================================================")
    test_deliverables_exist()
    test_source_id_correction_register()
    test_english_source_reconciliation()
    test_tanglish_linguistic_evaluation()
    test_governance_and_tokenizers()
    test_pytest_suites()
    print("\n==================================================================")
    print("  ALL PHASE 23B VERIFICATION CHECKS PASSED PERFECTLY (100%)")
    print("==================================================================")

if __name__ == "__main__":
    main()
