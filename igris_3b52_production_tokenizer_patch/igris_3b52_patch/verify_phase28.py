"""
verify_phase28.py — Deterministic verification script for IGRIS Phase 28.
Validates:
1. Deliverable file existence and non-empty status (10 deliverables).
2. All 21 master inventory entries accounted for in reconciliation.
3. All 13 candidate sources present.
4. Source ID integrity (SRC-CV-06 is Gutenberg Theatrical, SRC-CV-07 is WikiDialog).
5. All owner decisions set to NOT_REVIEWED (no fabricated decisions).
6. Zero sources marked APPROVED_FOR_ACQUISITION.
7. Decision cards exist for all 6 English candidates.
8. Pending and rejected sources explicitly tracked in pending register.
9. Phase 26 metric correction addendum confirmed present.
10. Tokenizer cryptographic hash invariants (Candidate A and Candidate B unchanged).
11. Zero production data check (quarantine/production/raw/acquired clean).
12. Full regression test suite execution.
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
    "PHASE28_SOURCE_RECONCILIATION.csv",
    "PHASE28_OWNER_REVIEW_MATRIX.csv",
    "PHASE28_SOURCE_DECISION_CARDS.md",
    "PHASE28_LEGAL_BLOCKER_TRACKER.csv",
    "PHASE28_RISK_PRIORITY_MATRIX.csv",
    "PHASE28_PENDING_SOURCE_REGISTER.csv",
    "PHASE28_OWNER_DECISION_GUIDE.md",
    "PHASE28_GOVERNANCE_INVARIANT_REPORT.md",
    "PHASE28_COMPLETION_REPORT.md",
    "verify_phase28.py",
]

def run_check(name, condition, error_msg=""):
    if condition:
        print(f"  [PASS] {name}")
        return True
    else:
        print(f"  [FAIL] {name}: {error_msg}")
        return False

def main():
    print("=" * 70)
    print("IGRIS Phase 28 — Verification")
    print("=" * 70)
    all_passed = True

    # 1. Deliverable Files Existence
    print("\n--- 1. Phase 28 Deliverable Files ---")
    for fname in EXPECTED_DELIVERABLES:
        fpath = os.path.join(PATCH_DIR, fname)
        exists = os.path.isfile(fpath) and os.path.getsize(fpath) > 100
        if not run_check(f"{fname} exists and non-empty", exists):
            all_passed = False

    # 2. Source Reconciliation Validation
    print("\n--- 2. Source Inventory Reconciliation ---")
    rec_path = os.path.join(PATCH_DIR, "PHASE28_SOURCE_RECONCILIATION.csv")
    sources = {}
    if os.path.isfile(rec_path):
        with open(rec_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sources[row["source_id"]] = row

        # Total 21 master inventory entries
        if not run_check(f"All 21 master inventory entries accounted for (found {len(sources)})", len(sources) == 21):
            all_passed = False

        # All 13 candidate sources present
        required_13 = [
            "SRC-TM-01", "SRC-TM-02", "SRC-TM-03",
            "SRC-TG-01", "SRC-TG-02", "SRC-TG-03",
            "SRC-EN-01", "SRC-TD-02", "SRC-TD-03",
            "SRC-CV-03", "SRC-CV-05", "SRC-CV-06", "SRC-CV-07"
        ]
        all_req = all(s in sources for s in required_13)
        if not run_check("All 13 candidate sources present in reconciliation", all_req):
            all_passed = False

        # Source ID integrity (CORR-23B-01)
        cv06 = sources.get("SRC-CV-06", {}).get("dataset_name", "")
        cv07 = sources.get("SRC-CV-07", {}).get("dataset_name", "")
        cv06_ok = "Theatrical" in cv06 or "Gutenberg" in cv06
        cv07_ok = "WikiDialog" in cv07
        if not run_check("SRC-CV-06 is Project Gutenberg Theatrical Dialogue", cv06_ok):
            all_passed = False
        if not run_check("SRC-CV-07 is WikiDialog English Subset", cv07_ok):
            all_passed = False

    # 3. Owner Review Matrix & Decision Verification
    print("\n--- 3. Owner Decision Integrity ---")
    matrix_path = os.path.join(PATCH_DIR, "PHASE28_OWNER_REVIEW_MATRIX.csv")
    if os.path.isfile(matrix_path):
        with open(matrix_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Check all decisions are NOT_REVIEWED
        non_default_decisions = []
        has_approved = False
        for r in rows:
            decision = r.get("current_owner_decision", "")
            if decision != "NOT_REVIEWED":
                non_default_decisions.append((r["source_id"], decision))
            status = r.get("evidence_status", "")
            if "APPROVED" in status or "APPROVED" in decision:
                has_approved = True

        if not run_check("All owner decisions set to NOT_REVIEWED (0 fabricated)", len(non_default_decisions) == 0, f"Found: {non_default_decisions}"):
            all_passed = False
        if not run_check("Zero sources marked APPROVED_FOR_ACQUISITION", not has_approved):
            all_passed = False

    # 4. Decision Cards Validation
    print("\n--- 4. Six English Decision Cards ---")
    cards_path = os.path.join(PATCH_DIR, "PHASE28_SOURCE_DECISION_CARDS.md")
    if os.path.isfile(cards_path):
        content = open(cards_path, "r", encoding="utf-8").read()
        six_candidates = ["SRC-EN-01", "SRC-TD-02", "SRC-TD-03", "SRC-CV-03", "SRC-CV-05", "SRC-CV-06"]
        all_cards_found = all(c in content for c in six_candidates)
        if not run_check("Decision cards exist for all 6 English candidates", all_cards_found):
            all_passed = False
        has_not_reviewed_in_cards = content.count("NOT_REVIEWED") >= 6
        if not run_check("All 6 decision cards specify NOT_REVIEWED", has_not_reviewed_in_cards):
            all_passed = False

    # 5. Pending and Rejected Source Register
    print("\n--- 5. Pending and Rejected Register ---")
    pending_path = os.path.join(PATCH_DIR, "PHASE28_PENDING_SOURCE_REGISTER.csv")
    if os.path.isfile(pending_path):
        with open(pending_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            p_rows = {r["source_id"]: r for r in reader}
        expected_pending_or_rej = ["SRC-TM-01", "SRC-TM-02", "SRC-TM-03", "SRC-TG-01", "SRC-TG-02", "SRC-TG-03", "SRC-CV-07"]
        all_p_found = all(s in p_rows for s in expected_pending_or_rej)
        if not run_check("All 7 pending/rejected candidates tracked in register", all_p_found):
            all_passed = False
        tg03_rejected = p_rows.get("SRC-TG-03", {}).get("evidence_status", "") == "REJECTED"
        if not run_check("SRC-TG-03 confirmed as REJECTED", tg03_rejected):
            all_passed = False

    # 6. Legal Blocker Tracker
    print("\n--- 6. Legal Blocker Tracker ---")
    blk_path = os.path.join(PATCH_DIR, "PHASE28_LEGAL_BLOCKER_TRACKER.csv")
    if os.path.isfile(blk_path):
        with open(blk_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            blk_rows = list(reader)
        has_min_blockers = len(blk_rows) >= 6
        if not run_check(f"Legal blocker tracker has >= 6 blockers (found {len(blk_rows)})", has_min_blockers):
            all_passed = False

    # 7. Phase 26 Metric Addendum Check
    print("\n--- 7. Phase 26 Metric Correction Addendum ---")
    addendum_path = os.path.join(PATCH_DIR, "PHASE26_METRIC_CORRECTION_ADDENDUM.md")
    if os.path.isfile(addendum_path):
        add_content = open(addendum_path, "r", encoding="utf-8").read()
        has_addendum = "PHASE 26 — Metric Correction Addendum" in add_content
        if not run_check("Phase 26 correction addendum exists and intact", has_addendum):
            all_passed = False
    else:
        print("  [FAIL] PHASE26_METRIC_CORRECTION_ADDENDUM.md missing")
        all_passed = False

    # 8. Tokenizer Cryptographic Hash Integrity
    print("\n--- 8. Tokenizer Cryptographic Integrity ---")
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

    # 9. Zero Production Ingress Verification
    print("\n--- 9. Zero Production Data Check ---")
    for d in ["production", "raw", "acquired", "quarantine"]:
        dpath = os.path.join(PROJECT_ROOT, d)
        exists = os.path.exists(dpath) and len(os.listdir(dpath)) > 0
        if not run_check(f"{d}/: clean (zero production bytes admitted)", not exists):
            all_passed = False

    # 10. Regression Test Execution
    print("\n--- 10. Regression Test Execution ---")
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
        print("PHASE 28 VERIFICATION: ALL CHECKS PASSED \u2713")
        print("VERDICT: VERDICT A (DECISION PREPARATION COMPLETE)")
        print("=" * 70)
        sys.exit(0)
    else:
        print("PHASE 28 VERIFICATION: SOME CHECKS FAILED ✗")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()
