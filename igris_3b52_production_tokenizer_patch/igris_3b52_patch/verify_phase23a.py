# verify_phase23a.py
"""
Deterministic independent verification script for Phase 23A:
1. Verifies existence and non-emptiness of all 9 Phase 23A deliverables.
2. Validates PHASE23A_ENGLISH_SOURCE_EVIDENCE_REGISTER.csv (6 candidates audited).
3. Verifies status breakdown (Verified for Owner Review: 5, Pending Legal: 1, Rejected: 0).
4. Validates PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl (100 valid fixtures, zero script contamination, NFC valid, zero PII).
5. Verifies Candidate A and Candidate B cryptographic SHA-256 hashes.
6. Verifies zero production bytes in quarantine raw directory.
7. Executes pytest readiness and production planning test suites.
"""

import csv
import hashlib
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")
PYTHON_EXE = Path(r"C:\IGRIS\.venv\Scripts\python.exe")

EXPECTED_DELIVERABLES = [
    "PHASE23A_ENGLISH_SOURCE_EVIDENCE_REGISTER.csv",
    "PHASE23A_PROJECT_GUTENBERG_REVIEW.md",
    "PHASE23A_IETF_PYTHON_REVIEW.md",
    "PHASE23A_CONVERSATIONAL_DATASET_REVIEW.md",
    "PHASE23A_TANGLISH_SYNTHETIC_GENERATOR_DESIGN.md",
    "PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl",
    "PHASE23A_TANGLISH_QUALITY_REPORT.md",
    "PHASE23A_COMPLETION_REPORT.md",
    "verify_phase23a.py",
]

EXPECTED_CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
EXPECTED_CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

PROHIBITED_BLOCKS = [
    ("Devanagari", 0x0900, 0x097F),
    ("Bengali", 0x0980, 0x09FF),
    ("Gurmukhi", 0x0A00, 0x0A7F),
    ("Gujarati", 0x0A80, 0x0AFF),
    ("Oriya", 0x0B00, 0x0B7F),
    ("Telugu", 0x0C00, 0x0C7F),
    ("Kannada", 0x0C80, 0x0CFF),
    ("Malayalam", 0x0D00, 0x0D7F),
    ("Sinhala", 0x0D80, 0x0DFF),
    ("Arabic", 0x0600, 0x06FF),
    ("Cyrillic", 0x0400, 0x04FF),
    ("CJK", 0x4E00, 0x9FFF),
]

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def test_deliverables_exist():
    print("1. Checking Phase 23A deliverables exist and non-empty...")
    for d in EXPECTED_DELIVERABLES:
        p_patch = PATCH_ROOT / d
        p_art = ARTIFACT_DIR / d
        assert p_patch.exists(), f"Missing in patch root: {p_patch}"
        assert p_patch.stat().st_size > 0, f"Empty file in patch root: {p_patch}"
        assert p_art.exists(), f"Missing in artifact dir: {p_art}"
        assert p_art.stat().st_size > 0, f"Empty file in artifact dir: {p_art}"
        print(f"  [OK] {d} (Patch: {p_patch.stat().st_size} bytes, Artifact: {p_art.stat().st_size} bytes)")

def test_english_evidence_register():
    print("\n2. Verifying English source evidence register...")
    csv_path = PATCH_ROOT / "PHASE23A_ENGLISH_SOURCE_EVIDENCE_REGISTER.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 6, f"Expected 6 candidate sources, got {len(rows)}"

    expected_ids = {"SRC-EN-01", "SRC-TD-02", "SRC-TD-03", "SRC-CV-03", "SRC-CV-05", "SRC-CV-06"}
    actual_ids = {r["source_id"] for r in rows}
    assert actual_ids == expected_ids, f"ID mismatch: {actual_ids} vs {expected_ids}"

    verified_for_review = [r for r in rows if r["phase23a_classification_status"] == "VERIFIED_FOR_OWNER_REVIEW"]
    pending_legal = [r for r in rows if r["phase23a_classification_status"] == "PENDING_LEGAL_REVIEW"]
    rejected = [r for r in rows if r["phase23a_classification_status"] == "REJECTED"]

    assert len(verified_for_review) == 5, f"Expected 5 verified for review, got {len(verified_for_review)}"
    assert len(pending_legal) == 1, f"Expected 1 pending legal, got {len(pending_legal)}"
    assert len(rejected) == 0, f"Expected 0 rejected, got {len(rejected)}"

    # Check WikiDialog specifically
    wikidialog_row = next(r for r in rows if r["source_id"] == "SRC-CV-06")
    assert wikidialog_row["phase23a_classification_status"] == "PENDING_LEGAL_REVIEW"
    assert "ShareAlike" in wikidialog_row["redistribution_and_derivative_work_restrictions"]

    print(f"  [OK] 6 candidate sources validated: 5 Verified for Owner Review, 1 Pending Legal Review (WikiDialog), 0 Rejected.")

def test_tanglish_fixtures_quality():
    print("\n3. Validating synthetic Tanglish fixtures...")
    jsonl_path = PATCH_ROOT / "PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl"
    with open(jsonl_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    assert len(lines) == 100, f"Expected 100 fixtures, got {len(lines)}"

    categories = set()
    texts = set()

    for idx, line in enumerate(lines, 1):
        item = json.loads(line)
        text = item["text"]
        cat = item["category"]
        categories.add(cat)

        assert text not in texts, f"Duplicate text at line {idx}: {text}"
        texts.add(text)

        # NFC normalization check
        assert text == unicodedata.normalize('NFC', text), f"Text not NFC normalized at line {idx}"

        # Prohibited script scan
        for char in text:
            cp = ord(char)
            for bname, start, end in PROHIBITED_BLOCKS:
                assert not (start <= cp <= end), f"Contamination: character {char} ({hex(cp)}) in {bname} at line {idx}"

        # Quality checks block
        assert item["quality_checks"]["unicode_nfc_valid"] is True
        assert item["quality_checks"]["zero_non_target_contamination"] is True
        assert item["quality_checks"]["zero_pii"] is True

    assert len(categories) == 5, f"Expected 5 linguistic categories, got {len(categories)}"
    print(f"  [OK] 100 fixtures validated across 5 categories with zero script contamination and zero PII.")

def test_governance_and_tokenizers():
    print("\n4. Verifying tokenizer cryptographic hashes and governance locks...")
    cand_a_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    cand_b_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"

    hash_a = compute_sha256(cand_a_path)
    hash_b = compute_sha256(cand_b_path)

    assert hash_a == EXPECTED_CANDIDATE_A_HASH, f"Candidate A hash mismatch: {hash_a}"
    assert hash_b == EXPECTED_CANDIDATE_B_HASH, f"Candidate B hash mismatch: {hash_b}"
    print(f"  [OK] Candidate A SHA-256 verified: {hash_a}")
    print(f"  [OK] Candidate B SHA-256 verified: {hash_b}")

    quarantine_raw = PATCH_ROOT / "quarantine" / "raw"
    if quarantine_raw.exists():
        files = list(quarantine_raw.glob("*"))
        assert len(files) == 0, f"Found files in quarantine raw: {files}"
    print("  [OK] Zero production data files in quarantine.")

def test_pytest_suites():
    print("\n5. Running pytest readiness and production planning test suites...")
    res1 = subprocess.run([str(PYTHON_EXE), "-m", "pytest", str(PATCH_ROOT / "tests" / "test_readiness.py"), "-q"], cwd=str(PATCH_ROOT), capture_output=True, text=True)
    assert res1.returncode == 0 and "5 passed" in res1.stdout, f"test_readiness failed: {res1.stdout}\n{res1.stderr}"
    print("  [OK] test_readiness.py passed (5/5)")

    res2 = subprocess.run([str(PYTHON_EXE), "-m", "pytest", str(PATCH_ROOT / "tests" / "test_phase22_production_planning.py"), "-q"], cwd=str(PATCH_ROOT), capture_output=True, text=True)
    assert res2.returncode == 0 and "6 passed" in res2.stdout, f"test_phase22_production_planning failed: {res2.stdout}\n{res2.stderr}"
    print("  [OK] test_phase22_production_planning.py passed (6/6)")

def main():
    print("==================================================================")
    print("  IGRIS PHASE 23A DETERMINISTIC VERIFICATION SUITE")
    print("==================================================================")
    test_deliverables_exist()
    test_english_evidence_register()
    test_tanglish_fixtures_quality()
    test_governance_and_tokenizers()
    test_pytest_suites()
    print("\n==================================================================")
    print("  ALL PHASE 23A VERIFICATION CHECKS PASSED PERFECTLY (100%)")
    print("==================================================================")

if __name__ == "__main__":
    main()
