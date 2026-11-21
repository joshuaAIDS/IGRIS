import csv
import hashlib
from pathlib import Path
import pytest

PATCH_ROOT = Path(__file__).resolve().parent.parent

CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

FOUR_CORE_ROLES = [
    "DATA_CUSTODIAN",
    "LEGAL_GOVERNANCE",
    "SECURITY_PRIVACY",
    "CHIEF_ARCHITECT",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_3c7_deliverables_exist():
    required_files = [
        "IGRIS_3C7_INTEGRITY_REPORT.md",
        "DATASET_SOURCE_CATALOG_V3.csv",
        "SOURCE_STATUS_RECONCILIATION.csv",
        "DATASET_LICENSE_EVIDENCE_V2.csv",
        "TOKENIZER_DATA_ELIGIBILITY_MATRIX.md",
        "GUTENBERG_ITEM_LEVEL_REVIEW.md",
        "IGRIS_3C7_STATUS.md",
    ]
    for rel_path in required_files:
        p = PATCH_ROOT / rel_path
        assert p.is_file(), f"Missing required 3C.7 file: {rel_path}"
        assert p.stat().st_size > 0, f"Empty 3C.7 file: {rel_path}"


def test_source_status_reconciliation_counts():
    csv_path = PATCH_ROOT / "SOURCE_STATUS_RECONCILIATION.csv"
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 32, f"Expected 32 sources in reconciliation, found {len(rows)}"

    statuses = [r["v3_primary_status"] for r in rows]
    from collections import Counter
    counts = Counter(statuses)

    assert counts["VERIFIED"] == 20, f"Expected 20 VERIFIED, got {counts['VERIFIED']}"
    assert counts["CONDITIONAL"] == 7, f"Expected 7 CONDITIONAL, got {counts['CONDITIONAL']}"
    assert counts["UNVERIFIED"] == 1, f"Expected 1 UNVERIFIED, got {counts['UNVERIFIED']}"
    assert counts["INCOMPATIBLE"] == 4, f"Expected 4 INCOMPATIBLE, got {counts['INCOMPATIBLE']}"
    assert sum(counts.values()) == 32

    for r in rows:
        assert r["source_id"].startswith("SRC-")
        assert len(r["reconciliation_explanation"].strip()) > 10


def test_dataset_source_catalog_v3_schema_and_boundaries():
    csv_path = PATCH_ROOT / "DATASET_SOURCE_CATALOG_V3.csv"
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 32, f"Expected 32 sources in V3 catalog, found {len(rows)}"

    expected_cols = [
        "source_id",
        "dataset_name",
        "category",
        "primary_language",
        "script",
        "dataset_owner_org",
        "official_source_url",
        "published_license",
        "license_verification_status",
        "commercial_use_evidence_status",
        "tokenizer_training_eligibility",
        "tokenizer_evaluation_eligibility",
        "alignment_safety_evaluation_eligibility",
        "published_size_estimate",
        "provenance_type",
        "pii_risk_level",
        "human_approval_status",
        "governance_notes",
    ]
    for col in expected_cols:
        assert col in reader.fieldnames, f"Missing expected column in V3: {col}"

    row_map = {r["source_id"]: r for r in rows}

    # Verify SRC-CV-04 boundary rules
    hh_rlhf = row_map["SRC-CV-04"]
    assert hh_rlhf["tokenizer_training_eligibility"] == "INELIGIBLE_PROHIBITED"
    assert hh_rlhf["tokenizer_evaluation_eligibility"] == "ELIGIBLE"
    assert hh_rlhf["alignment_safety_evaluation_eligibility"] == "ELIGIBLE_PRIMARY"

    # Verify SRC-CD-02 boundary rules
    humaneval = row_map["SRC-CD-02"]
    assert humaneval["tokenizer_training_eligibility"] == "INELIGIBLE_PROHIBITED"
    assert humaneval["tokenizer_evaluation_eligibility"] == "ELIGIBLE"

    # Verify 4 incompatible sources rejected across all pipelines
    incompatible_ids = ["SRC-TG-03", "SRC-HI-03", "SRC-CV-01", "SRC-CV-02"]
    for sid in incompatible_ids:
        assert row_map[sid]["tokenizer_training_eligibility"] == "INELIGIBLE_REJECTED"
        assert row_map[sid]["tokenizer_evaluation_eligibility"] == "INELIGIBLE_REJECTED"


def test_dataset_license_evidence_v2():
    csv_path = PATCH_ROOT / "DATASET_LICENSE_EVIDENCE_V2.csv"
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 32, f"Expected 32 sources in license evidence, found {len(rows)}"

    for r in rows:
        assert r["official_source_url"].startswith("http"), f"Invalid source URL for {r['source_id']}"
        assert r["evidence_url"].startswith("http"), f"Invalid evidence URL for {r['source_id']}"
        assert len(r["exact_license_and_version"].strip()) > 0
        assert len(r["commercial_use_evidence"].strip()) > 0


def test_gutenberg_item_level_review_content():
    content = (PATCH_ROOT / "GUTENBERG_ITEM_LEVEL_REVIEW.md").read_text(encoding="utf-8")
    assert "1928" in content, "Pre-1928 US rule must be specified"
    assert "Life + 70" in content or "Life+70" in content, "Life+70 rule must be specified"
    assert "1955" in content, "1955 author death cut-off must be specified"
    assert "trademark" in content.lower(), "Trademark requirements must be specified"
    assert "zero copyright risk globally" in content.lower(), "Must address and reject zero copyright risk globally"


def test_tokenizer_data_eligibility_matrix_content():
    content = (PATCH_ROOT / "TOKENIZER_DATA_ELIGIBILITY_MATRIX.md").read_text(encoding="utf-8")
    assert "SRC-CV-04" in content
    assert "SRC-CD-02" in content
    assert "poisoning" in content.lower() or "contamination" in content.lower()
    assert "32,768" in content


def test_four_approval_roles_preserved():
    matrix_text = (PATCH_ROOT / "TOKENIZER_DATA_ELIGIBILITY_MATRIX.md").read_text(encoding="utf-8")
    status_text = (PATCH_ROOT / "IGRIS_3C7_STATUS.md").read_text(encoding="utf-8")
    for role in FOUR_CORE_ROLES:
        assert role in matrix_text, f"Role {role} missing in TOKENIZER_DATA_ELIGIBILITY_MATRIX.md"
        assert role in status_text, f"Role {role} missing in IGRIS_3C7_STATUS.md"


def test_candidate_invariants_preserved():
    cand_a = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    cand_b = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
    assert cand_a.exists()
    assert cand_b.exists()
    assert sha256_file(cand_a) == CANDIDATE_A_HASH
    assert sha256_file(cand_b) == CANDIDATE_B_HASH
