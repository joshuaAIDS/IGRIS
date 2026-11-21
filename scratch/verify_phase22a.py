"""
scratch/verify_phase22a.py

Independent verification script for IGRIS Phase 22A deliverables and invariants.
"""

import os
import sys
import csv
import hashlib
import subprocess
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")
PYTHON_EXE = Path(r"C:\IGRIS\.venv\Scripts\python.exe")

EXPECTED_DELIVERABLES = [
    "PHASE22A_STORAGE_ARITHMETIC_RECONCILIATION.csv",
    "PHASE22A_STORAGE_LIFECYCLE_ANALYSIS.md",
    "PHASE22A_HARDWARE_VERIFICATION.md",
    "PHASE22A_TRAINING_DURATION_SCENARIOS.csv",
    "PHASE22A_CLOUD_COST_SCENARIOS.csv",
    "PHASE22A_COST_ASSUMPTIONS.md",
    "PHASE22A_TEST_EXECUTION_RECONCILIATION.md",
    "PHASE22A_COMPLETION_REPORT.md",
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
    print("Checking deliverables exist and non-empty...")
    for d in EXPECTED_DELIVERABLES:
        p_patch = PATCH_ROOT / d
        p_art = ARTIFACT_DIR / d
        assert p_patch.exists(), f"Missing in patch root: {p_patch}"
        assert p_patch.stat().st_size > 0, f"Empty file in patch root: {p_patch}"
        assert p_art.exists(), f"Missing in artifact dir: {p_art}"
        assert p_art.stat().st_size > 0, f"Empty file in artifact dir: {p_art}"
        print(f"  [OK] {d} (Patch: {p_patch.stat().st_size} bytes, Artifact: {p_art.stat().st_size} bytes)")

def test_storage_csv():
    print("\nChecking storage arithmetic reconciliation CSV...")
    csv_path = PATCH_ROOT / "PHASE22A_STORAGE_ARITHMETIC_RECONCILIATION.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    
    comp_map = {r["component_id"]: float(r["decimal_gb"]) for r in rows}
    assert comp_map["CAP_A_MIN_THEORETICAL"] == 260.00
    assert comp_map["CAP_B_PEAK_SIMULTANEOUS"] == 630.70
    assert comp_map["CAP_B_INPLACE_SIMULTANEOUS"] == 447.00
    assert comp_map["CAP_C_SEQUENTIAL_PEAK"] == 393.70
    assert comp_map["CAP_D_RECOMMENDED_1TB"] == 1000.00
    assert comp_map["HIST_PHASE22_REPORTED"] == 532.40
    print("  [OK] All storage reconciliation benchmark figures verified.")

def test_training_duration_csv():
    print("\nChecking training duration scenarios CSV...")
    csv_path = PATCH_ROOT / "PHASE22A_TRAINING_DURATION_SCENARIOS.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 20, f"Expected 20 scenario rows, got {len(rows)}"
    scen_ids = {r["scenario_id"] for r in rows}
    assert len(scen_ids) == 5
    print(f"  [OK] 20 scenario rows verified across {len(scen_ids)} distinct throughput configurations.")

def test_cloud_cost_csv():
    print("\nChecking cloud cost scenarios CSV...")
    csv_path = PATCH_ROOT / "PHASE22A_CLOUD_COST_SCENARIOS.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3, f"Expected 3 cost scenarios, got {len(rows)}"
    cost_map = {r["scenario_id"]: float(r["total_estimated_cost_usd"]) for r in rows}
    assert cost_map["COST_01_LOW_BUDGET"] == 33.36
    assert cost_map["COST_02_EXPECTED_ON_DEMAND"] == 109.14
    assert cost_map["COST_03_ENTERPRISE_TIER1"] == 293.54
    print("  [OK] All 3 cloud cost scenarios verified ($33.36, $109.14, $293.54).")

def test_tokenizer_hashes():
    print("\nChecking tokenizer physical hashes...")
    cand_a_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    cand_b_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
    
    hash_a = compute_sha256(cand_a_path)
    hash_b = compute_sha256(cand_b_path)
    
    assert hash_a == EXPECTED_CANDIDATE_A_HASH
    assert hash_b == EXPECTED_CANDIDATE_B_HASH
    print(f"  [OK] Candidate A SHA-256: {hash_a}")
    print(f"  [OK] Candidate B SHA-256: {hash_b}")

def test_readiness_and_phase22_suites():
    print("\nRunning test_readiness.py...")
    res1 = subprocess.run([str(PYTHON_EXE), "-m", "pytest", str(PATCH_ROOT / "tests" / "test_readiness.py"), "-q"], cwd=str(PATCH_ROOT), capture_output=True, text=True)
    assert res1.returncode == 0 and "5 passed" in res1.stdout
    print("  [OK] test_readiness.py passed (5/5)")

    print("Running test_phase22_production_planning.py...")
    res2 = subprocess.run([str(PYTHON_EXE), "-m", "pytest", str(PATCH_ROOT / "tests" / "test_phase22_production_planning.py"), "-q"], cwd=str(PATCH_ROOT), capture_output=True, text=True)
    assert res2.returncode == 0 and "6 passed" in res2.stdout
    print("  [OK] test_phase22_production_planning.py passed (6/6)")

def main():
    print("=== STARTING IGRIS PHASE 22A VERIFICATION ===")
    test_deliverables_exist()
    test_storage_csv()
    test_training_duration_csv()
    test_cloud_cost_csv()
    test_tokenizer_hashes()
    test_readiness_and_phase22_suites()
    print("\n=== ALL PHASE 22A VERIFICATIONS COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
