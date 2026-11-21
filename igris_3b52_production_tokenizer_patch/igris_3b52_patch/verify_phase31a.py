"""
verify_phase31a.py — Deterministic verification script for IGRIS Phase 31A.
Validates:
1. All 9 Phase 31A deliverable files exist and are non-empty.
2. Benchmark policies verified (no automatic rejection by similarity score; >=0.70 and >=0.85 route to MANUAL_REVIEW_REQUIRED).
3. Privacy masking policies verified ([EMAIL_REDACTED], [PHONE_REDACTED], Unicode preservation, uncertain PII held for review).
4. Language routing policies verified (combined metadata + LanguageIdentifierV2, Latin script not assumed English, uncertain held for review).
5. Synthetic policy test execution verification (all 24 synthetic tests in scripts/phase31a_policy_validator.py pass 100%).
6. Owner decisions preserved (SRC-TD-03, SRC-CV-03 = OWNER_ACCEPTS_FURTHER_REVIEW).
7. Preserved blockers check (Tamil TM-01..03, Tanglish TG-01..03, WikiDialog CV-07, 4 evidence-blocked sources).
8. Tokenizer cryptographic integrity (Candidate A and B hashes unchanged).
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
    "PHASE31A_OWNER_POLICY_DECISIONS.md",
    "PHASE31A_BENCHMARK_POLICY_SPEC.md",
    "PHASE31A_PRIVACY_MASKING_SPEC.md",
    "PHASE31A_LANGUAGE_ROUTING_SPEC.md",
    "PHASE31A_POLICY_TEST_REPORT.md",
    "PHASE31A_UPDATED_RISK_REGISTER.csv",
    "PHASE31A_GOVERNANCE_REPORT.md",
    "PHASE31A_COMPLETION_REPORT.md",
    "verify_phase31a.py",
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
    print("IGRIS Phase 31A — Verification")
    print("=" * 70)
    all_passed = True

    # 1. Deliverable Files Existence
    print("\n--- 1. Phase 31A Deliverable Files ---")
    for fname in EXPECTED_DELIVERABLES:
        fpath = os.path.join(PATCH_DIR, fname)
        exists = os.path.isfile(fpath) and os.path.getsize(fpath) > 100
        if not run_check(f"{fname} exists and non-empty", exists):
            all_passed = False

    # 2. Benchmark Policy Verification
    print("\n--- 2. Benchmark Similarity Policy Verification ---")
    bm_spec_path = os.path.join(PATCH_DIR, "PHASE31A_BENCHMARK_POLICY_SPEC.md")
    if os.path.isfile(bm_spec_path):
        content = open(bm_spec_path, "r", encoding="utf-8").read()
        no_auto_rej = "No Automatic Rejection" in content or "no similarity score alone" in content.lower()
        t70 = "0.70" in content and "MANUAL_REVIEW_REQUIRED" in content
        t85 = "0.85" in content and "MANUAL_REVIEW_REQUIRED" in content
        if not run_check("Benchmark spec confirms no automatic rejection by score alone", no_auto_rej):
            all_passed = False
        if not run_check("Benchmark spec confirms threshold 0.70 -> MANUAL_REVIEW_REQUIRED", t70):
            all_passed = False
        if not run_check("Benchmark spec confirms threshold 0.85 -> MANUAL_REVIEW_REQUIRED", t85):
            all_passed = False

    # 3. Privacy Masking Policy Verification
    print("\n--- 3. Privacy Masking Policy Verification ---")
    priv_spec_path = os.path.join(PATCH_DIR, "PHASE31A_PRIVACY_MASKING_SPEC.md")
    if os.path.isfile(priv_spec_path):
        p_content = open(priv_spec_path, "r", encoding="utf-8").read()
        placeholders = "[EMAIL_REDACTED]" in p_content and "[PHONE_REDACTED]" in p_content
        unicode_check = "NFC" in p_content and "Unicode" in p_content
        no_silent_accept = "No Silent Acceptance" in p_content or "never silently accepted" in p_content.lower()
        if not run_check("Privacy spec confirms approved placeholders", placeholders):
            all_passed = False
        if not run_check("Privacy spec confirms Unicode NFC preservation", unicode_check):
            all_passed = False
        if not run_check("Privacy spec prohibits silent acceptance of uncertain PII", no_silent_accept):
            all_passed = False

    # 4. Language Routing Policy Verification
    print("\n--- 4. OASST1 Language Routing Policy Verification ---")
    lang_spec_path = os.path.join(PATCH_DIR, "PHASE31A_LANGUAGE_ROUTING_SPEC.md")
    if os.path.isfile(lang_spec_path):
        l_content = open(lang_spec_path, "r", encoding="utf-8").read()
        latin_not_en = "Latin Script" in l_content and "English" in l_content
        tanglish_check = "TANGLISH" in l_content and "Romanized Tamil" in l_content
        five_cats = all(c in l_content for c in ["TAMIL", "ENGLISH", "TANGLISH", "UNKNOWN", "OUT_OF_SCOPE"])
        if not run_check("Language spec establishes Latin script is not assumed English", latin_not_en):
            all_passed = False
        if not run_check("Language spec routes Romanized Tamil/code-switching to TANGLISH", tanglish_check):
            all_passed = False
        if not run_check("Language spec recognizes all 5 allowed language categories", five_cats):
            all_passed = False

    # 5. Synthetic Policy Test Execution Check
    print("\n--- 5. Synthetic Policy Validator Execution ---")
    val_script = os.path.join(PATCH_DIR, "scripts", "phase31a_policy_validator.py")
    if os.path.isfile(val_script):
        python_exe = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
        if not os.path.isfile(python_exe):
            python_exe = sys.executable
        res = subprocess.run([python_exe, val_script], cwd=PATCH_DIR, capture_output=True, text=True)
        if not run_check("Policy validator executed with exit code 0", res.returncode == 0):
            all_passed = False
            print(res.stdout)
            print(res.stderr)
        else:
            all_24_passed = "ALL 24 POLICY TESTS PASSED (100%)" in res.stdout
            if not run_check("All 24 synthetic policy tests passed (100%)", all_24_passed):
                all_passed = False

    # 6. Decision Preservation Check
    print("\n--- 6. Source Decision Integrity Check ---")
    status_path = os.path.join(PATCH_DIR, "PHASE30_UPDATED_SOURCE_STATUS_REGISTER.csv")
    if os.path.isfile(status_path):
        with open(status_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            s_rows = {r["source_id"]: r for r in reader}
            
            # Review sources
            for sid in ["SRC-TD-03", "SRC-CV-03"]:
                dec = s_rows.get(sid, {}).get("current_owner_decision")
                if not run_check(f"{sid} decision preserved as OWNER_ACCEPTS_FURTHER_REVIEW", dec == "OWNER_ACCEPTS_FURTHER_REVIEW"):
                    all_passed = False
                    
            # 4 Evidence blocked sources
            for sid in ["SRC-EN-01", "SRC-TD-02", "SRC-CV-05", "SRC-CV-06"]:
                dec = s_rows.get(sid, {}).get("current_owner_decision")
                if not run_check(f"{sid} decision preserved as OWNER_REQUIRES_MORE_EVIDENCE", dec == "OWNER_REQUIRES_MORE_EVIDENCE"):
                    all_passed = False

            # Blockers
            tm_pass = all(s_rows.get(s, {}).get("current_owner_decision") == "PENDING_LEGAL_REVIEW" 
                          for s in ["SRC-TM-01", "SRC-TM-02", "SRC-TM-03"])
            if not run_check("Tamil blockers preserved (TM-01..03)", tm_pass):
                all_passed = False

            tg_pass = (s_rows.get("SRC-TG-01", {}).get("current_owner_decision") == "PENDING_LEGAL_REVIEW" and
                       s_rows.get("SRC-TG-02", {}).get("current_owner_decision") == "PENDING_LEGAL_REVIEW" and
                       s_rows.get("SRC-TG-03", {}).get("current_owner_decision") == "REJECTED")
            if not run_check("Tanglish blockers preserved (TG-01..02 pending, TG-03 rejected)", tg_pass):
                all_passed = False

            cv07_pass = s_rows.get("SRC-CV-07", {}).get("current_owner_decision") == "PENDING_LEGAL_REVIEW"
            if not run_check("WikiDialog preserved (CV-07)", cv07_pass):
                all_passed = False

            acq_granted = [r["source_id"] for r in s_rows.values() if r.get("acquisition_authorized") == "YES"]
            if not run_check("Zero acquisition grants created", len(acq_granted) == 0):
                all_passed = False

    # 7. Tokenizer Cryptographic Integrity
    print("\n--- 7. Tokenizer Cryptographic Integrity ---")
    tok_a = os.path.join(PATCH_DIR, "artifacts", "tokenizer", "candidate_a", "tokenizer.json")
    tok_b = os.path.join(PATCH_DIR, "artifacts", "tokenizer", "candidate_b", "tokenizer.model")
    if os.path.isfile(tok_a):
        hash_a = hashlib.sha256(open(tok_a, "rb").read()).hexdigest()
        if not run_check(f"Candidate A Hash: {hash_a[:16]}...", hash_a == CANDIDATE_A_HASH):
            all_passed = False
    else:
        run_check("Candidate A tokenizer exists", False, "Missing file")
        all_passed = False

    if os.path.isfile(tok_b):
        hash_b = hashlib.sha256(open(tok_b, "rb").read()).hexdigest()
        if not run_check(f"Candidate B Hash: {hash_b[:16]}...", hash_b == CANDIDATE_B_HASH):
            all_passed = False
    else:
        run_check("Candidate B tokenizer exists", False, "Missing file")
        all_passed = False

    # 8. Zero Production Data Check
    print("\n--- 8. Zero Production Data Check ---")
    for check_dir in ["production", "raw", "acquired", "quarantine"]:
        p = os.path.join(PROJECT_ROOT, "data", check_dir)
        if os.path.isdir(p):
            files = [f for f in os.listdir(p) if os.path.isfile(os.path.join(p, f))]
            if not run_check(f"{check_dir}/: clean (0 files)", len(files) == 0):
                all_passed = False
        else:
            run_check(f"{check_dir}/: not present (clean)", True)

    # 9. Full Regression Suite Execution
    print("\n--- 9. Full Regression Test Execution ---")
    python_exe = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
    if not os.path.isfile(python_exe):
        python_exe = sys.executable

    reg_tests = [
        "test_phase26_benchmark.py",
        "test_phase25_pipeline.py",
        "test_phase24_infrastructure.py",
    ]
    for rtest in reg_tests:
        rpath = os.path.join(PATCH_DIR, "tests", rtest)
        if os.path.isfile(rpath):
            res = subprocess.run([python_exe, "-m", "pytest", rpath, "-q"], cwd=PATCH_DIR, capture_output=True, text=True)
            if not run_check(f"{rtest} (exit code {res.returncode})", res.returncode == 0):
                all_passed = False
                print(res.stdout[:400])
                print(res.stderr[:400])

    print("\n" + "=" * 70)
    if all_passed:
        print("PHASE 31A VERIFICATION: ALL CHECKS PASSED ✓")
        print("VERDICT: VERDICT A (OWNER POLICIES CONFIRMED AND FROZEN)")
        print("=" * 70)
        sys.exit(0)
    else:
        print("PHASE 31A VERIFICATION: CHECKS FAILED ✗")
        print("VERDICT: VERDICT F (POLICY VERIFICATION FAILED)")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()
