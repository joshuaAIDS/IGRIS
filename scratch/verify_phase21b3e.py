"""
scratch/verify_phase21b3e.py

Independent verification script for IGRIS Phase 21B3E deliverables and governance invariants.
"""

import os
import sys
import hashlib
import csv
import subprocess
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")
PYTHON_EXE = Path(r"C:\IGRIS\.venv\Scripts\python.exe")

EXPECTED_DELIVERABLES = [
    "PHASE21B3E_TEST_ISOLATION_CODE_REVIEW.md",
    "PHASE21B3E_TEST_COLLECTION.txt",
    "PHASE21B3E_FULL_TEST_RESULTS.txt",
    "PHASE21B3E_TEST_SCOPE_RECONCILIATION.csv",
    "PHASE21B3E_TEST_REPRODUCTION_REPORT.md",
    "PHASE21B3E_POST_TEST_FILESYSTEM_AUDIT.md",
    "PHASE21B3E_INDICORP_OBJECT_IDENTITY.csv",
    "PHASE21B3E_OBJECT_IDENTITY_FINAL_STATUS.md",
    "PHASE21B3E_GOVERNANCE_INVARIANT_REPORT.md",
    "PHASE21B3E_COMPLETION_REPORT.md",
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

def test_tokenizer_hashes():
    print("\nChecking tokenizer physical hashes...")
    cand_a_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    cand_b_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
    
    assert cand_a_path.exists(), f"Candidate A missing: {cand_a_path}"
    assert cand_b_path.exists(), f"Candidate B missing: {cand_b_path}"
    
    hash_a = compute_sha256(cand_a_path)
    hash_b = compute_sha256(cand_b_path)
    
    assert hash_a == EXPECTED_CANDIDATE_A_HASH, f"Candidate A hash mismatch: got {hash_a}"
    assert hash_b == EXPECTED_CANDIDATE_B_HASH, f"Candidate B hash mismatch: got {hash_b}"
    print(f"  [OK] Candidate A SHA-256: {hash_a}")
    print(f"  [OK] Candidate B SHA-256: {hash_b}")

def test_indiccorp_csv():
    print("\nChecking IndicCorp object identity CSV...")
    csv_path = PATCH_ROOT / "PHASE21B3E_INDICORP_OBJECT_IDENTITY.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    
    assert len(reader) == 9, f"Expected 9 rows in CSV, got {len(reader)}"
    total_size = sum(int(row["declared_size_bytes"]) for row in reader)
    assert total_size == 183700000000, f"Expected total size 183700000000, got {total_size}"
    
    for row in reader:
        assert row["pinned_commit_sha"] == "984b75b20ce408f9ba27c6558e9279e8e1b6edfd"
        assert row["final_identity_status"] == "METADATA_ACCESSIBLE_PAYLOAD_UNINSPECTED"
        assert "NOT_EXPOSED" in row["git_blob_sha1"]
        assert "NOT_EXPOSED" in row["lfs_pointer_sha256_oid"]
    print(f"  [OK] 9 rows verified, total declared size: {total_size:,} bytes (183.70 GB decimal / 171.08 GiB binary)")
    print(f"  [OK] All files classified as METADATA_ACCESSIBLE_PAYLOAD_UNINSPECTED with 0 fabricated hashes")

def test_filesystem_cleanliness():
    print("\nChecking post-test filesystem cleanliness across patch root...")
    quarantine_dirs = []
    quarantine_files = []
    jsonl_files = []
    bin_files = []
    
    for root, dirs, files in os.walk(PATCH_ROOT):
        for d in dirs:
            if "quarantine" in d.lower():
                quarantine_dirs.append(os.path.join(root, d))
        for f in files:
            f_lower = f.lower()
            if "quarantine" in f_lower and not f_lower.endswith(".md"):
                quarantine_files.append(os.path.join(root, f))
            if f_lower.endswith(".jsonl"):
                jsonl_files.append(os.path.join(root, f))
            if f_lower.endswith((".parquet", ".bin", ".part", ".tar.gz")):
                bin_files.append(os.path.join(root, f))
                
    assert len(quarantine_dirs) == 0, f"Found quarantine dirs: {quarantine_dirs}"
    assert len(quarantine_files) == 0, f"Found quarantine files: {quarantine_files}"
    assert len(jsonl_files) == 0, f"Found jsonl audit logs: {jsonl_files}"
    assert len(bin_files) == 0, f"Found unapproved binary files: {bin_files}"
    print("  [OK] 0 quarantine dirs, 0 quarantine non-md files, 0 jsonl logs, 0 binary downloads")

def test_readiness_suite():
    print("\nExecuting independent readiness test (test_readiness.py)...")
    res = subprocess.run(
        [str(PYTHON_EXE), "-m", "pytest", str(PATCH_ROOT / "tests" / "test_readiness.py"), "-v"],
        cwd=str(PATCH_ROOT),
        capture_output=True,
        text=True
    )
    assert res.returncode == 0, f"Readiness test failed:\n{res.stdout}\n{res.stderr}"
    assert "5 passed" in res.stdout, f"Expected 5 passed, got:\n{res.stdout}"
    print("  [OK] test_readiness.py: 5 passed in isolated execution")

def main():
    print("=== STARTING IGRIS PHASE 21B3E VERIFICATION ===")
    test_deliverables_exist()
    test_tokenizer_hashes()
    test_indiccorp_csv()
    test_filesystem_cleanliness()
    test_readiness_suite()
    print("\n=== ALL PHASE 21B3E VERIFICATIONS COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
