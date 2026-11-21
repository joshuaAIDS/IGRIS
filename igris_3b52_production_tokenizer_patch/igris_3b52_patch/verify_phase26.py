#!/usr/bin/env python3
"""
IGRIS Phase 26 — Deterministic Automated Verification Script.
Validates deliverables, dataset splits non-leakage, test suites, tokenizer hashes,
resource benchmarks, and governance invariants.
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
    print("IGRIS Phase 26 — Verification")
    print("=" * 70)

    # 1. Deliverables existence
    print("\n--- 1. Phase 26 Deliverable Files ---")
    deliverables = [
        "PHASE26_BENCHMARK_DESIGN.md",
        "PHASE26_DATASET_SPLITS.json",
        "PHASE26_LANGUAGE_IDENTIFICATION_REPORT.md",
        "PHASE26_TANGLISH_EVALUATION_REPORT.md",
        "PHASE26_UNICODE_BENCHMARK_REPORT.md",
        "PHASE26_QUALITY_FILTER_REPORT.md",
        "PHASE26_DUPLICATE_BENCHMARK_REPORT.md",
        "PHASE26_TOKENIZER_COMPARISON_REPORT.md",
        "PHASE26_PERFORMANCE_REPORT.md",
        "PHASE26_METRIC_RECONCILIATION_REPORT.md",
        "PHASE26_TEST_RESULTS.json",
        "PHASE26_COMPLETION_REPORT.md",
        "verify_phase26.py",
    ]
    for d in deliverables:
        p = PATCH_DIR / d
        check(p.exists() and p.stat().st_size > 100, f"{d} exists and non-empty")

    # 2. Dataset Splits Non-Leakage Check
    print("\n--- 2. Dataset Splits Integrity & Non-Leakage ---")
    splits_p = PATCH_DIR / "PHASE26_DATASET_SPLITS.json"
    if splits_p.exists():
        data = json.loads(splits_p.read_text(encoding="utf-8"))
        dev_t = set(r["text"] for r in data["splits"]["dev"])
        val_t = set(r["text"] for r in data["splits"]["val"])
        test_t = set(r["text"] for r in data["splits"]["test"])
        check(len(data["splits"]["dev"]) == 100, "dev split contains 100 records")
        check(len(data["splits"]["val"]) == 100, "val split contains 100 records")
        check(len(data["splits"]["test"]) == 100, "test split contains 100 records")
        check(len(dev_t & val_t) == 0, "Zero leakage between dev and val")
        check(len(dev_t & test_t) == 0, "Zero leakage between dev and test")
        check(len(val_t & test_t) == 0, "Zero leakage between val and test")
    else:
        for _ in range(6):
            check(False, "Dataset splits file missing")

    # 3. Phase 26 Unit & Integration Tests
    print("\n--- 3. Phase 26 Benchmark Tests ---")
    r26 = subprocess.run(
        [VENV_PYTHON, "-m", "pytest", "tests/test_phase26_benchmark.py", "-v", "--tb=short"],
        capture_output=True, text=True, cwd=str(PATCH_DIR), timeout=60,
    )
    passed26 = r26.stdout.count(" PASSED")
    check(r26.returncode == 0, f"test_phase26_benchmark.py (exit code {r26.returncode}, {passed26} passed)")

    # 4. Phase 25 Regression Tests
    print("\n--- 4. Phase 25 Regression Tests ---")
    r25 = subprocess.run(
        [VENV_PYTHON, "-m", "pytest", "tests/test_phase25_pipeline.py", "-v", "--tb=short"],
        capture_output=True, text=True, cwd=str(PATCH_DIR), timeout=60,
    )
    passed25 = r25.stdout.count(" PASSED")
    check(r25.returncode == 0, f"test_phase25_pipeline.py (exit code {r25.returncode}, {passed25} passed)")

    # 5. Phase 24 Regression Tests
    print("\n--- 5. Phase 24 Regression Tests ---")
    r24 = subprocess.run(
        [VENV_PYTHON, "-m", "pytest", "tests/test_phase24_infrastructure.py", "-v", "--tb=short"],
        capture_output=True, text=True, cwd=str(PATCH_DIR), timeout=60,
    )
    passed24 = r24.stdout.count(" PASSED")
    check(r24.returncode == 0, f"test_phase24_infrastructure.py (exit code {r24.returncode}, {passed24} passed)")

    # 6. Project Regression Suites
    print("\n--- 6. Project Regression Suites ---")
    for s in ["tests/test_readiness.py", "tests/test_phase22_production_planning.py"]:
        rs = subprocess.run(
            [VENV_PYTHON, "-m", "pytest", s, "-v", "--tb=short"],
            capture_output=True, text=True, cwd=str(PATCH_DIR), timeout=60,
        )
        passed_s = rs.stdout.count(" PASSED")
        check(rs.returncode == 0, f"{s} (exit code {rs.returncode}, {passed_s} passed)")

    # 7. Tokenizer Cryptographic Integrity
    print("\n--- 7. Tokenizer Cryptographic Integrity ---")
    tok_a = PATCH_DIR / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    h_a = hashlib.sha256(open(tok_a, "rb").read()).hexdigest()
    check(h_a == "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561", f"Candidate A Hash: {h_a[:16]}...")

    tok_b = PATCH_DIR / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
    h_b = hashlib.sha256(open(tok_b, "rb").read()).hexdigest()
    check(h_b == "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888", f"Candidate B Hash: {h_b[:16]}...")

    # 8. Zero Production Data Check
    print("\n--- 8. Zero Production Data Check ---")
    for pd in [PATCH_DIR / "data" / "production", PATCH_DIR / "data" / "raw", PATCH_DIR / "data" / "acquired"]:
        if pd.exists():
            files = [f for f in pd.rglob("*") if f.is_file() and f.suffix not in {".md", ".txt", ".gitkeep"}]
            check(len(files) == 0, f"{pd.name}/: {len(files)} production files (expected 0)")
        else:
            check(True, f"{pd.name}/: does not exist (0 files)")

    # Final Summary
    print("\n" + "=" * 70)
    total = PASS + FAIL
    print(f"PHASE 26 VERIFICATION: {PASS}/{total} checks passed, {FAIL} failed")
    if FAIL == 0:
        print("VERDICT: ALL CHECKS PASSED ✓")
    else:
        print(f"VERDICT: {FAIL} CHECK(S) FAILED ✗")
    print("=" * 70)
    return 0 if FAIL == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
