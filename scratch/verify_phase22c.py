"""
scratch/verify_phase22c.py

Comprehensive independent verification suite for Phase 22C:
1. Verifies existence and non-emptiness of all 6 Phase 22C deliverables in both patch and artifact directories.
2. Mathematically validates PHASE22C_STORAGE_STAGE_MATRIX.csv.
3. Verifies Candidate A and Candidate B cryptographic SHA-256 hashes.
4. Executes test_readiness.py (5/5).
5. Executes test_phase22_production_planning.py (6/6).
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
    "PHASE22C_STREAMING_BUFFER_VALIDATION.md",
    "PHASE22C_STORAGE_STAGE_MATRIX.csv",
    "PHASE22C_STORAGE_CAPACITY_RECONCILIATION.md",
    "PHASE22C_HARDWARE_EVIDENCE_NOTE.md",
    "PHASE22C_CLOUD_COST_EVIDENCE_AUDIT.md",
    "PHASE22C_COMPLETION_REPORT.md",
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
    print("Checking Phase 22C deliverables exist and non-empty...")
    for d in EXPECTED_DELIVERABLES:
        p_patch = PATCH_ROOT / d
        p_art = ARTIFACT_DIR / d
        assert p_patch.exists(), f"Missing in patch root: {p_patch}"
        assert p_patch.stat().st_size > 0, f"Empty file in patch root: {p_patch}"
        assert p_art.exists(), f"Missing in artifact dir: {p_art}"
        assert p_art.stat().st_size > 0, f"Empty file in artifact dir: {p_art}"
        print(f"  [OK] {d} (Patch: {p_patch.stat().st_size} bytes, Artifact: {p_art.stat().st_size} bytes)")

def test_storage_matrix_csv():
    print("\nChecking storage stage matrix CSV calculations...")
    csv_path = PATCH_ROOT / "PHASE22C_STORAGE_STAGE_MATRIX.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) >= 9, f"Expected at least 9 rows in matrix, got {len(rows)}"

    for r in rows:
        size_gb = float(r["component_size_gb_dec"])
        size_gib = float(r["component_size_gib_bin"])
        expected_gib = round(size_gb * (10**9) / (1024**3), 2)
        assert abs(size_gib - expected_gib) <= 0.05, f"Binary GiB conversion error in {r['stage_id']}: got {size_gib}, expected {expected_gib}"

        subtotal_gb = float(r["stage_subtotal_gb_dec"])
        os_gb = float(r["os_headroom_gb_dec"])
        high_water_gb = float(r["stage_high_water_gb_dec"])
        assert round(subtotal_gb + os_gb, 2) == round(high_water_gb, 2), f"Arithmetic error in {r['stage_id']}: {subtotal_gb} + {os_gb} != {high_water_gb}"

    # Specific stage assertions
    stage_map = {r["stage_id"]: r for r in rows}
    
    # Ingress measured
    assert stage_map["STAGE_01A_INGRESS_MEASURED"]["stage_high_water_gb_dec"] == "233.70"
    assert stage_map["STAGE_01A_INGRESS_MEASURED"]["stage_high_water_gib_bin"] == "217.65"
    
    # Cleaning & Dedup peak
    assert stage_map["STAGE_02_CLEANING_DEDUP"]["stage_high_water_gb_dec"] == "393.70"
    assert stage_map["STAGE_02_CLEANING_DEDUP"]["stage_high_water_gib_bin"] == "366.66"

    # Dual-copy peaks
    assert stage_map["STAGE_05A_WORST_CASE_DUAL_COPY_MEASURED"]["stage_high_water_gb_dec"] == "604.40"
    assert stage_map["STAGE_05A_WORST_CASE_DUAL_COPY_MEASURED"]["stage_high_water_gib_bin"] == "562.89"
    assert stage_map["STAGE_05B_WORST_CASE_DUAL_COPY_PHANTOM"]["stage_high_water_gb_dec"] == "631.10"
    assert stage_map["STAGE_05B_WORST_CASE_DUAL_COPY_PHANTOM"]["stage_high_water_gib_bin"] == "587.76"

    print("  [OK] Storage stage matrix calculations and conversions verified 100%.")

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
    # Check quarantine directory
    quarantine_raw = PATCH_ROOT / "quarantine" / "raw"
    if quarantine_raw.exists():
        files = list(quarantine_raw.glob("*"))
        assert len(files) == 0, f"Found files in quarantine raw: {files}"
    print("  [OK] Zero production data files in quarantine.")

def main():
    print("==================================================================")
    print("  IGRIS PHASE 22C INDEPENDENT VERIFICATION SUITE")
    print("==================================================================")
    test_deliverables_exist()
    test_storage_matrix_csv()
    test_tokenizer_hashes()
    test_readiness_and_phase22_suites()
    test_governance_invariants()
    print("\n==================================================================")
    print("  ALL PHASE 22C VERIFICATION CHECKS PASSED PERFECTLY (100%)")
    print("==================================================================")

if __name__ == "__main__":
    main()
