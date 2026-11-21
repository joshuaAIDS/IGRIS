"""
scratch/verify_phase22b.py

Independent verification script for IGRIS Phase 22B deliverables, calculations, and invariants.
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
    "PHASE22B_HARDWARE_EVIDENCE_CORRECTION.md",
    "PHASE22B_STORAGE_STAGE_MATRIX.csv",
    "PHASE22B_STORAGE_LIFECYCLE_CORRECTION.md",
    "PHASE22B_TRAINING_THROUGHPUT_AUDIT.csv",
    "PHASE22B_CLOUD_COST_RECONCILIATION.csv",
    "PHASE22B_CLOUD_COST_EVIDENCE.md",
    "PHASE22B_TEST_EVIDENCE.md",
    "PHASE22B_COMPLETION_REPORT.md",
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

def test_storage_matrix_csv():
    print("\nChecking storage stage matrix CSV...")
    csv_path = PATCH_ROOT / "PHASE22B_STORAGE_STAGE_MATRIX.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    
    stage_map = {r["stage_id"]: float(r["total_stage_gb"]) for r in rows}
    assert stage_map["STAGE_01_INGRESS"] == 260.40
    assert stage_map["STAGE_02_CLEANING"] == 393.70
    assert stage_map["STAGE_03_TOKENIZATION"] == 212.00
    assert stage_map["STAGE_04_PRETRAINING"] == 87.00
    assert stage_map["HIGH_WATER_SEQUENTIAL_PEAK"] == 393.70
    assert stage_map["PEAK_CONSERVATIVE_DUAL_COPY"] == 631.10
    assert stage_map["RECOMMENDED_1TB_PROVISION"] == 1000.00
    print("  [OK] Storage stage matrix calculations and high-water peaks verified.")

def test_throughput_audit_csv():
    print("\nChecking training throughput audit CSV...")
    csv_path = PATCH_ROOT / "PHASE22B_TRAINING_THROUGHPUT_AUDIT.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 20, f"Expected 20 scenario rows, got {len(rows)}"
    
    # Check mathematical accuracy of hours
    for r in rows:
        eff_rate = float(r["effective_tok_sec"])
        eff_hrs = float(r["effective_hours"])
        tok_str = r["token_target"]
        if "1B" in tok_str:
            tokens = 1_000_000_000
        elif "3B" in tok_str:
            tokens = 3_000_000_000
        elif "5.5B" in tok_str:
            tokens = 5_500_000_000
        else:
            tokens = 10_000_000_000
        expected_hrs = round(tokens / (eff_rate * 3600), 2)
        assert abs(eff_hrs - expected_hrs) <= 0.05, f"Hours mismatch for {r['rate_id']} {tok_str}: got {eff_hrs}, expected {expected_hrs}"
    print("  [OK] All 20 throughput scenario calculations verified mathematically.")

def test_cloud_cost_csv():
    print("\nChecking cloud cost reconciliation CSV...")
    csv_path = PATCH_ROOT / "PHASE22B_CLOUD_COST_RECONCILIATION.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3, f"Expected 3 cost scenarios, got {len(rows)}"
    for r in rows:
        train_h = float(r["pure_training_hours_5_5b"])
        prep_h = float(r["data_prep_hours"])
        billed_h = float(r["total_billed_compute_hours"])
        assert round(train_h + prep_h, 2) == round(billed_h, 2), f"Duration mismatch: {train_h} + {prep_h} != {billed_h}"
    print("  [OK] Cloud cost durations and itemized overheads verified.")

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
    print("=== STARTING IGRIS PHASE 22B VERIFICATION ===")
    test_deliverables_exist()
    test_storage_matrix_csv()
    test_throughput_audit_csv()
    test_cloud_cost_csv()
    test_tokenizer_hashes()
    test_readiness_and_phase22_suites()
    print("\n=== ALL PHASE 22B VERIFICATIONS COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
