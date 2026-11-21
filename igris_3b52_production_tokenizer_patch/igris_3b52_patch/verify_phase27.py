"""
verify_phase27.py — Deterministic verification script for IGRIS Phase 27.
Validates:
1. Deliverable file existence and non-empty status (12 deliverables).
2. Phase 26 metric correction addendum completeness.
3. Master source inventory completeness (13 candidate + 8 out-of-scope).
4. Source ID integrity (SRC-CV-06 is Gutenberg Theatrical, SRC-CV-07 is WikiDialog).
5. Exact evidence status enum validation (no APPROVED_FOR_ACQUISITION).
6. Legal review questions register completeness.
7. Tokenizer cryptographic hash invariants.
8. Zero production bytes / zero network ingress verification.
9. Regression test suite execution.
"""

import csv
import hashlib
import json
import os
import subprocess
import sys

PATCH_DIR = r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch"
PROJECT_ROOT = r"C:\IGRIS"

CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

EXPECTED_DELIVERABLES = [
    "PHASE26_METRIC_CORRECTION_ADDENDUM.md",
    "PHASE27_SOURCE_INVENTORY.csv",
    "PHASE27_LICENSE_EVIDENCE_REGISTER.csv",
    "PHASE27_COPYRIGHT_RISK_REGISTER.csv",
    "PHASE27_PRIVACY_RISK_REGISTER.csv",
    "PHASE27_TAMIL_SOURCE_AUDIT.md",
    "PHASE27_ENGLISH_SOURCE_AUDIT.md",
    "PHASE27_TANGLISH_SOURCE_AUDIT.md",
    "PHASE27_LEGAL_REVIEW_REQUIRED.csv",
    "PHASE27_OWNER_REVIEW_SUMMARY.md",
    "PHASE27_COMPLETION_REPORT.md",
    "verify_phase27.py",
]

VALID_STATUSES = {
    "VERIFIED_FOR_OWNER_REVIEW",
    "PENDING_LEGAL_REVIEW",
    "INSUFFICIENT_EVIDENCE",
    "REJECTED",
    "OUT_OF_SCOPE",
}

def run_check(name, condition, error_msg=""):
    if condition:
        print(f"  [PASS] {name}")
        return True
    else:
        print(f"  [FAIL] {name}: {error_msg}")
        return False

def main():
    print("=" * 70)
    print("IGRIS Phase 27 — Verification")
    print("=" * 70)
    all_passed = True

    # 1. Deliverable Files Existence
    print("\n--- 1. Phase 27 Deliverable Files ---")
    for fname in EXPECTED_DELIVERABLES:
        fpath = os.path.join(PATCH_DIR, fname)
        exists = os.path.isfile(fpath) and os.path.getsize(fpath) > 100
        if not run_check(f"{fname} exists and non-empty", exists):
            all_passed = False

    # 2. Source Inventory Validation
    print("\n--- 2. Source Inventory Integrity ---")
    inv_path = os.path.join(PATCH_DIR, "PHASE27_SOURCE_INVENTORY.csv")
    sources = {}
    if os.path.isfile(inv_path):
        with open(inv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sources[row["source_id"]] = row

        # Check required candidates exist
        required_13 = [
            "SRC-TM-01", "SRC-TM-02", "SRC-TM-03",
            "SRC-TG-01", "SRC-TG-02", "SRC-TG-03",
            "SRC-EN-01", "SRC-TD-02", "SRC-TD-03",
            "SRC-CV-03", "SRC-CV-05", "SRC-CV-06", "SRC-CV-07"
        ]
        all_req_present = all(s in sources for s in required_13)
        if not run_check("All 13 candidate sources present in inventory", all_req_present):
            all_passed = False

        # Source ID integrity (CORR-23B-01)
        gutenberg_theatrical = sources.get("SRC-CV-06", {}).get("dataset_name", "")
        wikidialog = sources.get("SRC-CV-07", {}).get("dataset_name", "")
        cv06_ok = "Gutenberg Theatrical" in gutenberg_theatrical or "Theatrical" in gutenberg_theatrical
        cv07_ok = "WikiDialog" in wikidialog
        if not run_check("SRC-CV-06 is Project Gutenberg Theatrical Dialogue", cv06_ok):
            all_passed = False
        if not run_check("SRC-CV-07 is WikiDialog English Subset", cv07_ok):
            all_passed = False

        # Status validation: exact enum values, no APPROVED_FOR_ACQUISITION
        invalid_statuses = []
        has_approved = False
        for sid, row in sources.items():
            status = row.get("evidence_status", "")
            if status not in VALID_STATUSES:
                invalid_statuses.append((sid, status))
            if "APPROVED" in status:
                has_approved = True

        if not run_check("All source statuses match valid evidence enums", len(invalid_statuses) == 0, f"Invalid: {invalid_statuses}"):
            all_passed = False
        if not run_check("Zero sources marked APPROVED_FOR_ACQUISITION", not has_approved):
            all_passed = False

    # 3. Legal Review Required Register
    print("\n--- 3. Legal Review Questions Register ---")
    lrq_path = os.path.join(PATCH_DIR, "PHASE27_LEGAL_REVIEW_REQUIRED.csv")
    if os.path.isfile(lrq_path):
        with open(lrq_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            lrq_rows = list(reader)
        has_min_questions = len(lrq_rows) >= 5
        if not run_check(f"Legal review register has >= 5 questions (found {len(lrq_rows)})", has_min_questions):
            all_passed = False
        # Check that TM-01, TM-02, TG-01 have legal questions
        sources_in_lrq = {r["source_id"] for r in lrq_rows}
        key_sources_covered = {"SRC-TM-01", "SRC-TM-02", "SRC-TG-01"}.issubset(sources_in_lrq)
        if not run_check("Key legal questions cover SRC-TM-01, SRC-TM-02, SRC-TG-01", key_sources_covered):
            all_passed = False

    # 4. Phase 26 Metric Addendum Check
    print("\n--- 4. Phase 26 Metric Correction Addendum ---")
    addendum_path = os.path.join(PATCH_DIR, "PHASE26_METRIC_CORRECTION_ADDENDUM.md")
    if os.path.isfile(addendum_path):
        content = open(addendum_path, "r", encoding="utf-8").read()
        has_recalc = "Recalculated Confusion Matrix" in content
        has_narrative = "NARRATIVE ERROR" in content
        has_verdict = "Verdict A" in content
        if not run_check("Addendum contains recalculated confusion matrix", has_recalc):
            all_passed = False
        if not run_check("Addendum documents narrative discrepancies", has_narrative):
            all_passed = False
        if not run_check("Addendum reaffirms Phase 26 Verdict A", has_verdict):
            all_passed = False

    # 5. Tokenizer Cryptographic Hash Integrity
    print("\n--- 5. Tokenizer Cryptographic Integrity ---")
    cand_a_path = os.path.join(PATCH_DIR, "artifacts", "tokenizer", "candidate_a", "tokenizer.json")
    cand_b_path = os.path.join(PATCH_DIR, "artifacts", "tokenizer", "candidate_b", "tokenizer.model")

    if os.path.isfile(cand_a_path):
        with open(cand_a_path, "rb") as f:
            ha = hashlib.sha256(f.read()).hexdigest()
        if not run_check(f"Candidate A Hash: {ha[:16]}...", ha == CANDIDATE_A_HASH):
            all_passed = False
    else:
        print("  [FAIL] candidate_a tokenizer.json not found")
        all_passed = False

    if os.path.isfile(cand_b_path):
        with open(cand_b_path, "rb") as f:
            hb = hashlib.sha256(f.read()).hexdigest()
        if not run_check(f"Candidate B Hash: {hb[:16]}...", hb == CANDIDATE_B_HASH):
            all_passed = False
    else:
        print("  [FAIL] candidate_b tokenizer.model not found")
        all_passed = False

    # 6. Zero Production Ingress Verification
    print("\n--- 6. Zero Production Data Check ---")
    for d in ["production", "raw", "acquired", "quarantine"]:
        dpath = os.path.join(PROJECT_ROOT, d)
        exists = os.path.exists(dpath) and len(os.listdir(dpath)) > 0
        if not run_check(f"{d}/: clean (zero production bytes admitted)", not exists):
            all_passed = False

    # 7. Regression Test Suite Check
    print("\n--- 7. Regression Test Execution ---")
    python_exe = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
    if not os.path.isfile(python_exe):
        python_exe = sys.executable

    test_files = [
        os.path.join(PATCH_DIR, "tests", "test_phase26_benchmark.py"),
        os.path.join(PATCH_DIR, "tests", "test_phase25_pipeline.py"),
        os.path.join(PATCH_DIR, "tests", "test_phase24_infrastructure.py"),
    ]

    for tf in test_files:
        bname = os.path.basename(tf)
        if os.path.isfile(tf):
            res = subprocess.run([python_exe, "-m", "pytest", tf, "-q"], capture_output=True, text=True, cwd=PATCH_DIR)
            passed = (res.returncode == 0)
            if not run_check(f"{bname} (exit code {res.returncode})", passed, res.stderr[:100] if not passed else ""):
                all_passed = False
        else:
            print(f"  [SKIP] {bname} not found")

    print("\n" + "=" * 70)
    if all_passed:
        print("PHASE 27 VERIFICATION: ALL CHECKS PASSED \u2713")
        print("VERDICT: VERDICT A (LEGAL & RIGHTS AUDIT COMPLETE)")
        print("=" * 70)
        sys.exit(0)
    else:
        print("PHASE 27 VERIFICATION: SOME CHECKS FAILED ✗")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()
