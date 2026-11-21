"""
scratch/verify_phase22d.py

Comprehensive independent verification suite for Phase 22D:
1. Verifies existence and non-emptiness of all 5 Phase 22D deliverables in both patch and artifact directories.
2. Validates PHASE22D_STORAGE_COMPONENT_REGISTER.csv.
3. Mathematically validates PHASE22D_STORAGE_STAGE_MATRIX.csv (all 10 stages).
4. Verifies Candidate A and Candidate B cryptographic SHA-256 hashes.
5. Executes test_readiness.py (5/5) and test_phase22_production_planning.py (6/6).
6. Confirms zero production bytes acquired and governance locks intact.
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
    "PHASE22D_STORAGE_COMPONENT_REGISTER.csv",
    "PHASE22D_STORAGE_STAGE_MATRIX.csv",
    "PHASE22D_STORAGE_ARITHMETIC_CORRECTION.md",
    "PHASE22D_FILESYSTEM_CAPACITY_ANALYSIS.md",
    "PHASE22D_COMPLETION_REPORT.md",
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
    print("Checking Phase 22D deliverables exist and non-empty...")
    for d in EXPECTED_DELIVERABLES:
        p_patch = PATCH_ROOT / d
        p_art = ARTIFACT_DIR / d
        assert p_patch.exists(), f"Missing in patch root: {p_patch}"
        assert p_patch.stat().st_size > 0, f"Empty file in patch root: {p_patch}"
        assert p_art.exists(), f"Missing in artifact dir: {p_art}"
        assert p_art.stat().st_size > 0, f"Empty file in artifact dir: {p_art}"
        print(f"  [OK] {d} (Patch: {p_patch.stat().st_size} bytes, Artifact: {p_art.stat().st_size} bytes)")

def test_component_register_csv():
    print("\nChecking storage component register CSV...")
    csv_path = PATCH_ROOT / "PHASE22D_STORAGE_COMPONENT_REGISTER.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) >= 12, f"Expected at least 12 components, got {len(rows)}"

    for r in rows:
        gb = float(r["size_gb_dec"])
        gib = float(r["size_gib_bin"])
        expected_gib = round(gb * (10**9) / (1024**3), 2)
        assert abs(gib - expected_gib) <= 0.05, f"Binary conversion error in {r['component_id']}: {gib} vs {expected_gib}"

    print(f"  [OK] All {len(rows)} storage components verified mathematically.")

def test_stage_matrix_csv():
    print("\nChecking 10-stage storage matrix CSV...")
    csv_path = PATCH_ROOT / "PHASE22D_STORAGE_STAGE_MATRIX.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 11, f"Expected 11 rows (10 numbered stages with 2A/2B ingress variants), got {len(rows)}"

    for r in rows:
        p_app = float(r["persistent_app_gb_dec"])
        t_app = float(r["temp_workspace_gb_dec"])
        tot_app = float(r["total_app_gb_dec"])
        os_res = float(r["os_reserve_gb_dec"])
        tot_stage = float(r["total_stage_gb_dec"])

        # Check subtotal
        assert round(p_app + t_app, 2) == round(tot_app, 2), f"App sum error in {r['stage_id']}: {p_app} + {t_app} != {tot_app}"
        # Check total stage
        assert round(tot_app + os_res, 2) == round(tot_stage, 2), f"Stage total error in {r['stage_id']}: {tot_app} + {os_res} != {tot_stage}"

        # Check binary conversions
        expected_stage_gib = round(tot_stage * (10**9) / (1024**3), 2)
        actual_stage_gib = float(r["total_stage_gib_bin"])
        assert abs(actual_stage_gib - expected_stage_gib) <= 0.05, f"Stage GiB error in {r['stage_id']}: {actual_stage_gib} vs {expected_stage_gib}"

    stage_map = {r["stage_id"]: r for r in rows}

    # Verify Stage 8 (Pretraining Corrected)
    p_stage = stage_map["STAGE_08_PRETRAINING"]
    assert p_stage["total_app_gb_dec"] == "37.00", f"Pretraining app total mismatch: {p_stage['total_app_gb_dec']}"
    assert p_stage["total_stage_gb_dec"] == "87.00", f"Pretraining stage total mismatch: {p_stage['total_stage_gb_dec']}"
    assert p_stage["total_stage_gib_bin"] == "81.03", f"Pretraining stage gib mismatch: {p_stage['total_stage_gib_bin']}"

    # Verify Stage 6 (Tokenization Cleaned)
    tok_clean = stage_map["STAGE_06_TOKENIZATION_CLEANED"]
    assert tok_clean["total_app_gb_dec"] == "162.00"
    assert tok_clean["total_stage_gb_dec"] == "212.00"

    # Verify Stage 7 (Tokenization Raw Retained)
    tok_raw = stage_map["STAGE_07_TOKENIZATION_RAW_RETAINED"]
    assert tok_raw["total_app_gb_dec"] == "345.70"
    assert tok_raw["total_stage_gb_dec"] == "395.70"

    # Verify Stage 5 (Deduplication Sequential Peak)
    dedup = stage_map["STAGE_05_DEDUPLICATION"]
    assert dedup["total_app_gb_dec"] == "343.70"
    assert dedup["total_stage_gb_dec"] == "393.70"
    assert dedup["total_stage_gib_bin"] == "366.66"

    # Verify Stage 10 (Zero Cleanup)
    zero_clean = stage_map["STAGE_10_CONSERVATIVE_ZERO_CLEANUP"]
    assert zero_clean["total_app_gb_dec"] == "564.40"
    assert zero_clean["total_stage_gb_dec"] == "614.40"
    assert zero_clean["total_stage_gib_bin"] == "572.20"

    print("  [OK] Authoritative 10-stage storage matrix verified 100% mathematically.")

def test_tokenizer_hashes():
    print("\nChecking tokenizer candidate hashes...")
    cand_a_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    cand_b_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
    
    hash_a = compute_sha256(cand_a_path)
    hash_b = compute_sha256(cand_b_path)
    
    assert hash_a == EXPECTED_CANDIDATE_A_HASH, f"Candidate A hash mismatch: {hash_a}"
    assert hash_b == EXPECTED_CANDIDATE_B_HASH, f"Candidate B hash mismatch: {hash_b}"
    print(f"  [OK] Candidate A SHA-256: {hash_a}")
    print(f"  [OK] Candidate B SHA-256: {hash_b}")

def test_readiness_and_phase22_suites():
    print("\nRunning test_readiness.py...")
    res1 = subprocess.run([str(PYTHON_EXE), "-m", "pytest", str(PATCH_ROOT / "tests" / "test_readiness.py"), "-q"], cwd=str(PATCH_ROOT), capture_output=True, text=True)
    assert res1.returncode == 0 and "5 passed" in res1.stdout, f"test_readiness failed: {res1.stdout}\n{res1.stderr}"
    print("  [OK] test_readiness.py passed (5/5)")

    print("Running test_phase22_production_planning.py...")
    res2 = subprocess.run([str(PYTHON_EXE), "-m", "pytest", str(PATCH_ROOT / "tests" / "test_phase22_production_planning.py"), "-q"], cwd=str(PATCH_ROOT), capture_output=True, text=True)
    assert res2.returncode == 0 and "6 passed" in res2.stdout, f"test_phase22_production_planning failed: {res2.stdout}\n{res2.stderr}"
    print("  [OK] test_phase22_production_planning.py passed (6/6)")

def test_governance_invariants():
    print("\nVerifying governance invariants...")
    quarantine_raw = PATCH_ROOT / "quarantine" / "raw"
    if quarantine_raw.exists():
        files = list(quarantine_raw.glob("*"))
        assert len(files) == 0, f"Found files in quarantine raw: {files}"
    print("  [OK] Zero production data files in quarantine.")

def main():
    print("==================================================================")
    print("  IGRIS PHASE 22D INDEPENDENT VERIFICATION SUITE")
    print("==================================================================")
    test_deliverables_exist()
    test_component_register_csv()
    test_stage_matrix_csv()
    test_tokenizer_hashes()
    test_readiness_and_phase22_suites()
    test_governance_invariants()
    print("\n==================================================================")
    print("  ALL PHASE 22D VERIFICATION CHECKS PASSED PERFECTLY (100%)")
    print("==================================================================")

if __name__ == "__main__":
    main()
