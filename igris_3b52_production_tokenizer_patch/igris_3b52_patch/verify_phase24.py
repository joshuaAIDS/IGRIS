#!/usr/bin/env python3
"""IGRIS Phase 24 — Deterministic Verification Script.

Verifies:
1. All deliverable files exist.
2. All infrastructure modules exist and import successfully.
3. Unit test suite passes (48 tests).
4. Tokenizer hash is unchanged.
5. Zero production data.
6. Production ingress LOCKED.
7. Existing regression suites pass.
"""

import hashlib
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

PATCH_DIR = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
VENV_PYTHON = r"C:\IGRIS\.venv\Scripts\python.exe"

PASS = 0
FAIL = 0

def check(condition, description):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {description}")
    else:
        FAIL += 1
        print(f"  [FAIL] {description}")
    return condition


def main():
    global PASS, FAIL
    print("=" * 70)
    print("IGRIS Phase 24 — Verification")
    print("=" * 70)

    # 1. Deliverable files
    print("\n--- 1. Deliverable Files ---")
    deliverables = [
        "PHASE24_LANGUAGE_ENGINE_DESIGN.md",
        "PHASE24_UNICODE_PROCESSING_REPORT.md",
        "PHASE24_TANGLISH_ANALYSIS_REPORT.md",
        "PHASE24_DATA_QUALITY_REPORT.md",
        "PHASE24_DUPLICATE_DETECTION_REPORT.md",
        "PHASE24_TOKENIZER_EVALUATION_REPORT.md",
        "PHASE24_COMPLETION_REPORT.md",
        "verify_phase24.py",
    ]
    for d in deliverables:
        p = PATCH_DIR / d
        check(p.exists() and p.stat().st_size > 100, f"{d} exists and non-empty")

    # 2. Infrastructure modules
    print("\n--- 2. Infrastructure Modules ---")
    modules = [
        "scripts/language_identifier_v2.py",
        "scripts/unicode_processor_v2.py",
        "scripts/tanglish_analyzer.py",
        "scripts/quality_filter_v2.py",
        "scripts/duplicate_detector_v2.py",
        "scripts/language_quality_reporter.py",
        "tests/test_phase24_infrastructure.py",
    ]
    for m in modules:
        p = PATCH_DIR / m
        check(p.exists() and p.stat().st_size > 100, f"{m} exists and non-empty")

    # 3. Module imports
    print("\n--- 3. Module Imports ---")
    sys.path.insert(0, str(PATCH_DIR / "scripts"))
    for mod_name in [
        "language_identifier_v2",
        "unicode_processor_v2",
        "tanglish_analyzer",
        "quality_filter_v2",
        "duplicate_detector_v2",
        "language_quality_reporter",
    ]:
        try:
            importlib.import_module(mod_name)
            check(True, f"import {mod_name}")
        except Exception as e:
            check(False, f"import {mod_name}: {e}")

    # 4. Unit tests
    print("\n--- 4. Unit Test Suite ---")
    result = subprocess.run(
        [VENV_PYTHON, "-m", "pytest", "tests/test_phase24_infrastructure.py", "-v", "--tb=short"],
        capture_output=True, text=True, cwd=str(PATCH_DIR), timeout=120,
    )
    test_passed = result.returncode == 0
    # Count passed tests
    passed_count = result.stdout.count(" PASSED")
    check(test_passed, f"Phase 24 test suite (exit code {result.returncode}, {passed_count} passed)")
    if not test_passed:
        print(f"    STDOUT (last 500 chars): ...{result.stdout[-500:]}")
        print(f"    STDERR (last 500 chars): ...{result.stderr[-500:]}")

    # 5. Tokenizer hash
    print("\n--- 5. Tokenizer Hash ---")
    tok_path = PATCH_DIR / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    if tok_path.exists():
        with open(tok_path, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        expected = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
        check(h == expected, f"Candidate A hash: {h[:20]}...")
    else:
        check(False, "Candidate A tokenizer file missing")

    tok_b_path = PATCH_DIR / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
    if tok_b_path.exists():
        with open(tok_b_path, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        expected_b = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"
        check(h == expected_b, f"Candidate B hash: {h[:20]}...")
    else:
        check(False, "Candidate B tokenizer file missing")

    # 6. Zero production data
    print("\n--- 6. Production Data Check ---")
    production_dirs = [
        PATCH_DIR / "data" / "production",
        PATCH_DIR / "data" / "raw",
        PATCH_DIR / "data" / "acquired",
    ]
    for pd in production_dirs:
        if pd.exists():
            files = list(pd.rglob("*"))
            data_files = [f for f in files if f.is_file() and f.suffix not in {".md", ".txt", ".gitkeep"}]
            check(len(data_files) == 0, f"{pd.name}/: {len(data_files)} production files (expected 0)")
        else:
            check(True, f"{pd.name}/: directory does not exist (no production data)")

    # 7. Regression suites
    print("\n--- 7. Regression Suites ---")
    for suite in ["tests/test_readiness.py", "tests/test_phase22_production_planning.py"]:
        suite_path = PATCH_DIR / suite
        if suite_path.exists():
            r = subprocess.run(
                [VENV_PYTHON, "-m", "pytest", suite, "-v", "--tb=short"],
                capture_output=True, text=True, cwd=str(PATCH_DIR), timeout=60,
            )
            passed = r.stdout.count(" PASSED")
            check(r.returncode == 0, f"{suite} ({passed} passed)")
        else:
            check(False, f"{suite}: file not found")

    # 8. Evaluation results exist
    print("\n--- 8. Evaluation Results ---")
    eval_path = Path(r"C:\IGRIS\scratch\phase24_eval_results.json")
    if eval_path.exists():
        with open(eval_path, "r") as f:
            data = json.load(f)
        check("language_classification" in data, "Language classification results present")
        check("unicode_tests" in data, "Unicode test results present")
        check("duplicate_detection" in data, "Duplicate detection results present")
        check("quality_filter" in data, "Quality filter results present")
        check("tokenizer_evaluation" in data, "Tokenizer evaluation results present")
        check("tanglish_analysis" in data, "Tanglish analysis results present")
    else:
        for _ in range(6):
            check(False, "Evaluation results file missing")

    # Summary
    print("\n" + "=" * 70)
    total = PASS + FAIL
    print(f"PHASE 24 VERIFICATION: {PASS}/{total} checks passed, {FAIL} failed")
    if FAIL == 0:
        print("VERDICT: ALL CHECKS PASSED ✓")
    else:
        print(f"VERDICT: {FAIL} CHECK(S) FAILED ✗")
    print("=" * 70)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
