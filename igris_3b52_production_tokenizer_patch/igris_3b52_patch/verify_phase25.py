#!/usr/bin/env python3
"""
IGRIS Phase 25 — Deterministic Verification Script.
Validates deliverables, tests, tokenizer hashes, reproducibility, and governance.
"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

PATCH_DIR = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
VENV_PYTHON = r"C:\IGRIS\.venv\Scripts\python.exe"

PASS = 0
FAIL = 0

def check(condition, desc):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {desc}")
    else:
        FAIL += 1
        print(f"  [FAIL] {desc}")
    return condition

def main():
    global PASS, FAIL
    print("=" * 70)
    print("IGRIS Phase 25 — Verification")
    print("=" * 70)

    # 1. Deliverables existence
    print("\n--- 1. Phase 25 Deliverable Files ---")
    deliverables = [
        "PHASE25_PIPELINE_ARCHITECTURE.md",
        "PHASE25_SYNTHETIC_DATASET_MANIFEST.json",
        "PHASE25_LANGUAGE_IDENTIFICATION_REPORT.md",
        "PHASE25_UNICODE_VALIDATION_REPORT.md",
        "PHASE25_DATA_QUALITY_REPORT.md",
        "PHASE25_DUPLICATE_DETECTION_REPORT.md",
        "PHASE25_REPRODUCIBILITY_REPORT.md",
        "PHASE25_TOKENIZER_EVALUATION_REPORT.md",
        "PHASE25_TEST_RESULTS.json",
        "PHASE25_COMPLETION_REPORT.md",
        "verify_phase25.py",
        "PHASE25_SYNTHETIC_BENCHMARK_FIXTURES.jsonl",
    ]
    for d in deliverables:
        p = PATCH_DIR / d
        check(p.exists() and p.stat().st_size > 100, f"{d} exists and non-empty")

    # 2. Pipeline module import
    print("\n--- 2. Pipeline Module Import ---")
    sys.path.insert(0, str(PATCH_DIR / "scripts"))
    try:
        import dataset_pipeline_v2
        check(True, "import dataset_pipeline_v2")
    except Exception as e:
        check(False, f"import dataset_pipeline_v2: {e}")

    # 3. Phase 25 Unit & Integration Tests
    print("\n--- 3. Phase 25 Unit & Integration Tests ---")
    r25 = subprocess.run(
        [VENV_PYTHON, "-m", "pytest", "tests/test_phase25_pipeline.py", "-v", "--tb=short"],
        capture_output=True, text=True, cwd=str(PATCH_DIR), timeout=60,
    )
    passed25 = r25.stdout.count(" PASSED")
    check(r25.returncode == 0, f"test_phase25_pipeline.py (exit code {r25.returncode}, {passed25} passed)")

    # 4. Phase 24 Regression Tests
    print("\n--- 4. Phase 24 Regression Tests ---")
    r24 = subprocess.run(
        [VENV_PYTHON, "-m", "pytest", "tests/test_phase24_infrastructure.py", "-v", "--tb=short"],
        capture_output=True, text=True, cwd=str(PATCH_DIR), timeout=60,
    )
    passed24 = r24.stdout.count(" PASSED")
    check(r24.returncode == 0, f"test_phase24_infrastructure.py (exit code {r24.returncode}, {passed24} passed)")

    # 5. Project Regression Suites
    print("\n--- 5. Project Regression Suites ---")
    for s in ["tests/test_readiness.py", "tests/test_phase22_production_planning.py"]:
        rs = subprocess.run(
            [VENV_PYTHON, "-m", "pytest", s, "-v", "--tb=short"],
            capture_output=True, text=True, cwd=str(PATCH_DIR), timeout=60,
        )
        passed_s = rs.stdout.count(" PASSED")
        check(rs.returncode == 0, f"{s} (exit code {rs.returncode}, {passed_s} passed)")

    # 6. Tokenizer Hashes (Read-Only)
    print("\n--- 6. Tokenizer Cryptographic Integrity ---")
    tok_a = PATCH_DIR / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    h_a = hashlib.sha256(open(tok_a, "rb").read()).hexdigest()
    check(h_a == "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561", f"Candidate A Hash: {h_a[:16]}...")

    tok_b = PATCH_DIR / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
    h_b = hashlib.sha256(open(tok_b, "rb").read()).hexdigest()
    check(h_b == "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888", f"Candidate B Hash: {h_b[:16]}...")

    # 7. Zero Production Data
    print("\n--- 7. Zero Production Data Check ---")
    for pd in [PATCH_DIR / "data" / "production", PATCH_DIR / "data" / "raw", PATCH_DIR / "data" / "acquired"]:
        if pd.exists():
            files = [f for f in pd.rglob("*") if f.is_file() and f.suffix not in {".md", ".txt", ".gitkeep"}]
            check(len(files) == 0, f"{pd.name}/: {len(files)} production files (expected 0)")
        else:
            check(True, f"{pd.name}/: does not exist (0 files)")

    # 8. Manifest Integrity Check
    print("\n--- 8. Manifest Integrity Check ---")
    manifest_p = PATCH_DIR / "PHASE25_SYNTHETIC_DATASET_MANIFEST.json"
    if manifest_p.exists():
        data = json.loads(manifest_p.read_text(encoding="utf-8"))
        check("records" in data and len(data["records"]) == 150, "Manifest contains exactly 150 records")
        check("summary_telemetry" in data, "Manifest contains summary telemetry")
    else:
        check(False, "Manifest file missing")

    # Final Summary
    print("\n" + "=" * 70)
    total = PASS + FAIL
    print(f"PHASE 25 VERIFICATION: {PASS}/{total} checks passed, {FAIL} failed")
    if FAIL == 0:
        print("VERDICT: ALL CHECKS PASSED ✓")
    else:
        print(f"VERDICT: {FAIL} CHECK(S) FAILED ✗")
    print("=" * 70)
    return 0 if FAIL == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
