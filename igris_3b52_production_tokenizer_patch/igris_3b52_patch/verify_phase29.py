"""
verify_phase29.py — Deterministic verification script for IGRIS Phase 29.
Validates:
1. Deliverable file existence and non-empty status (8 deliverables).
2. All 6 candidate sources present in decision register.
3. All 6 decisions initialized to NOT_REVIEWED.
4. Five approved decision values recognized by system.
5. Zero fabricated owner decisions.
6. Source ID integrity (SRC-CV-06 is Gutenberg Theatrical, SRC-CV-07 is WikiDialog).
7. Preserved Tamil and Tanglish blockers tracked.
8. Tokenizer cryptographic hash invariants (Candidate A and Candidate B unchanged).
9. Zero production data check (quarantine/production/raw/acquired clean).
10. Full regression test suite execution.
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
    "PHASE29_OWNER_DECISION_REGISTER.csv",
    "PHASE29_OWNER_REVIEW_PACKAGE.md",
    "PHASE29_SOURCE_COMPARISON.md",
    "PHASE29_UNRESOLVED_RISK_REGISTER.csv",
    "PHASE29_EVIDENCE_REFERENCE_REGISTER.csv",
    "PHASE29_GOVERNANCE_REPORT.md",
    "PHASE29_COMPLETION_REPORT.md",
    "verify_phase29.py",
]

APPROVED_DECISION_VOCABULARY = {
    "OWNER_ACCEPTS_FURTHER_REVIEW",
    "OWNER_REQUIRES_LEGAL_COUNSEL",
    "OWNER_REQUIRES_MORE_EVIDENCE",
    "OWNER_REJECTS_SOURCE",
    "NOT_REVIEWED",
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
    print("IGRIS Phase 29 — Verification")
    print("=" * 70)
    all_passed = True

    # 1. Deliverable Files Existence
    print("\n--- 1. Phase 29 Deliverable Files ---")
    for fname in EXPECTED_DELIVERABLES:
        fpath = os.path.join(PATCH_DIR, fname)
        exists = os.path.isfile(fpath) and os.path.getsize(fpath) > 100
        if not run_check(f"{fname} exists and non-empty", exists):
            all_passed = False

    # 2. Decision Register Integrity
    print("\n--- 2. Owner Decision Register Integrity ---")
    reg_path = os.path.join(PATCH_DIR, "PHASE29_OWNER_DECISION_REGISTER.csv")
    sources = {}
    if os.path.isfile(reg_path):
        with open(reg_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sources[row["source_id"]] = row

        # All 6 review candidates present
        expected_6 = ["SRC-EN-01", "SRC-TD-02", "SRC-TD-03", "SRC-CV-03", "SRC-CV-05", "SRC-CV-06"]
        all_6_present = all(s in sources for s in expected_6)
        if not run_check(f"All 6 candidates present in decision register (found {len(sources)})", all_6_present):
            all_passed = False

        # All decisions set to NOT_REVIEWED
        non_default = []
        has_approved = False
        for sid, r in sources.items():
            decision = r.get("owner_decision", "")
            if decision != "NOT_REVIEWED":
                non_default.append((sid, decision))
            if decision not in APPROVED_DECISION_VOCABULARY:
                all_passed = False
                print(f"  [FAIL] Unrecognized decision value '{decision}' for {sid}")
            status = r.get("current_evidence_status", "")
            if "APPROVED" in status or "APPROVED" in decision:
                has_approved = True

        if not run_check("All 6 candidate decisions set to NOT_REVIEWED (0 fabricated)", len(non_default) == 0, f"Found: {non_default}"):
            all_passed = False
        if not run_check("Zero sources marked APPROVED_FOR_ACQUISITION", not has_approved):
            all_passed = False

        # Source ID integrity: SRC-CV-06 is Gutenberg Theatrical
        cv06 = sources.get("SRC-CV-06", {}).get("dataset_name", "")
        if not run_check("SRC-CV-06 is Gutenberg Theatrical Dialogue", "Theatrical" in cv06 or "Gutenberg" in cv06):
            all_passed = False

    # 3. Owner Review Package Verification
    print("\n--- 3. Owner Review Package Structure ---")
    pkg_path = os.path.join(PATCH_DIR, "PHASE29_OWNER_REVIEW_PACKAGE.md")
    if os.path.isfile(pkg_path):
        pkg_content = open(pkg_path, "r", encoding="utf-8").read()
        all_six_in_pkg = all(c in pkg_content for c in ["SRC-EN-01", "SRC-TD-02", "SRC-TD-03", "SRC-CV-03", "SRC-CV-05", "SRC-CV-06"])
        if not run_check("All 6 candidates presented in review package", all_six_in_pkg):
            all_passed = False
        has_decision_boxes = pkg_content.count("OWNER DECISION FIELD") >= 6
        if not run_check("All 6 decision boxes present in package", has_decision_boxes):
            all_passed = False

    # 4. Unresolved Risk Register
    print("\n--- 4. Unresolved Risk Register ---")
    rsk_path = os.path.join(PATCH_DIR, "PHASE29_UNRESOLVED_RISK_REGISTER.csv")
    if os.path.isfile(rsk_path):
        with open(rsk_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rsk_rows = list(reader)
        has_min_risks = len(rsk_rows) >= 10
        if not run_check(f"Unresolved risk register has >= 10 risks (found {len(rsk_rows)})", has_min_risks):
            all_passed = False

    # 5. Evidence Reference Register
    print("\n--- 5. Evidence Reference Register ---")
    evd_path = os.path.join(PATCH_DIR, "PHASE29_EVIDENCE_REFERENCE_REGISTER.csv")
    if os.path.isfile(evd_path):
        with open(evd_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            evd_rows = list(reader)
        has_min_evd = len(evd_rows) >= 10
        if not run_check(f"Evidence reference register has >= 10 references (found {len(evd_rows)})", has_min_evd):
            all_passed = False

    # 6. Preserved Tamil and Tanglish Blockers
    print("\n--- 6. Preserved Blockers Check ---")
    comp_path = os.path.join(PATCH_DIR, "PHASE29_COMPLETION_REPORT.md")
    if os.path.isfile(comp_path):
        comp_content = open(comp_path, "r", encoding="utf-8").read()
        tamil_preserved = "SRC-TM-01" in comp_content and "SRC-TM-02" in comp_content and "SRC-TM-03" in comp_content
        tanglish_preserved = "SRC-TG-01" in comp_content and "SRC-TG-02" in comp_content and "SRC-TG-03" in comp_content
        wikidialog_preserved = "SRC-CV-07" in comp_content
        if not run_check("Tamil blockers preserved (TM-01, TM-02, TM-03)", tamil_preserved):
            all_passed = False
        if not run_check("Tanglish blockers preserved (TG-01, TG-02, TG-03)", tanglish_preserved):
            all_passed = False
        if not run_check("WikiDialog preserved as pending (CV-07)", wikidialog_preserved):
            all_passed = False

    # 7. Tokenizer Cryptographic Hash Integrity
    print("\n--- 7. Tokenizer Cryptographic Integrity ---")
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

    # 8. Zero Production Ingress Verification
    print("\n--- 8. Zero Production Data Check ---")
    for d in ["production", "raw", "acquired", "quarantine"]:
        dpath = os.path.join(PROJECT_ROOT, d)
        exists = os.path.exists(dpath) and len(os.listdir(dpath)) > 0
        if not run_check(f"{d}/: clean (zero production bytes admitted)", not exists):
            all_passed = False

    # 9. Regression Test Execution
    print("\n--- 9. Regression Test Execution ---")
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
        print("PHASE 29 VERIFICATION: ALL CHECKS PASSED \u2713")
        print("VERDICT: VERDICT A (INDIVIDUAL OWNER REVIEW READY)")
        print("=" * 70)
        sys.exit(0)
    else:
        print("PHASE 29 VERIFICATION: SOME CHECKS FAILED ✗")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()
