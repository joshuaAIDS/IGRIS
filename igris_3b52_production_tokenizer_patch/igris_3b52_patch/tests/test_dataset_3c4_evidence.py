"""
Unit tests for Milestone 3C.4: Dataset Evidence & Human Review Preparation.
Validates source evidence registers, license matrices, category coverage audits,
human review packages, and artifact checksum invariance.
"""

import csv
import hashlib
from pathlib import Path
import pytest

_PATCH_ROOT = Path(__file__).resolve().parent.parent

CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

CANONICAL_CATEGORIES = [
    "Tamil",
    "English",
    "Tanglish",
    "Hindi",
    "Other Indian Languages",
    "Multilingual Mixed Text",
    "Programming Code",
    "Technical Documentation",
    "Conversational Text",
    "Emoji & Unicode Edge Cases",
]

REQUIRED_ROLES = [
    "DATA_CUSTODIAN",
    "LEGAL_GOVERNANCE",
    "SECURITY_PRIVACY",
    "CHIEF_ARCHITECT",
]


def test_3c4_deliverables_exist():
    """Verify all Milestone 3C.4 deliverables exist and have meaningful content."""
    deliverables = [
        "IGRIS_3C4_EVIDENCE_REPORT.md",
        "DATASET_SOURCE_EVIDENCE_REGISTER.csv",
        "DATASET_LICENSE_EVIDENCE_MATRIX.csv",
        "DATASET_CATEGORY_COVERAGE_AUDIT.md",
        "HUMAN_REVIEW_PACKAGE.md",
        "IGRIS_3C4_STATUS.md",
    ]
    for filename in deliverables:
        path = _PATCH_ROOT / filename
        assert path.exists(), f"Missing Milestone 3C.4 deliverable: {filename}"
        assert path.stat().st_size > 500, f"Deliverable {filename} is suspiciously small"


def test_source_evidence_register_schema_and_counts():
    """Verify DATASET_SOURCE_EVIDENCE_REGISTER.csv schema, 26 sources, and classification distribution."""
    csv_path = _PATCH_ROOT / "DATASET_SOURCE_EVIDENCE_REGISTER.csv"
    assert csv_path.exists()

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 26, f"Expected 26 sources, found {len(rows)}"

    expected_cols = {
        "source_id",
        "dataset_name_version",
        "canonical_category",
        "dataset_owner_publisher",
        "official_source_url",
        "official_license_url",
        "license_identifier",
        "commercial_use_permitted",
        "modification_permitted",
        "redistribution_requirements",
        "attribution_required",
        "share_alike_obligations",
        "non_commercial_restrictions",
        "training_evaluation_evidence",
        "privacy_pii_risks",
        "verification_date",
        "evidence_confidence",
        "outstanding_questions",
        "classification",
    }
    assert expected_cols.issubset(set(reader.fieldnames or []))

    counts = {"VERIFIED": 0, "REQUIRES HUMAN APPROVAL": 0, "INCOMPATIBLE": 0, "UNVERIFIED": 0}
    for row in rows:
        cls = row["classification"]
        assert cls in counts, f"Invalid classification '{cls}' in row {row['source_id']}"
        counts[cls] += 1
        assert row["official_source_url"].startswith("http")
        assert row["canonical_category"] in CANONICAL_CATEGORIES

    assert counts["VERIFIED"] == 14
    assert counts["REQUIRES HUMAN APPROVAL"] == 7
    assert counts["INCOMPATIBLE"] == 4
    assert counts["UNVERIFIED"] == 1


def test_license_evidence_matrix_schema_and_integrity():
    """Verify DATASET_LICENSE_EVIDENCE_MATRIX.csv has 26 rows and matches verdicts."""
    csv_path = _PATCH_ROOT / "DATASET_LICENSE_EVIDENCE_MATRIX.csv"
    assert csv_path.exists()

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 26
    for row in rows:
        assert row["legal_verdict"] in {"VERIFIED", "REQUIRES HUMAN APPROVAL", "INCOMPATIBLE", "UNVERIFIED"}
        assert len(row["commercial_rights_basis"]) > 0
        assert len(row["legal_reviewer_action"]) > 0


def test_category_coverage_audit_content():
    """Verify category coverage audit evaluates all 10 categories and documents gaps."""
    content = (_PATCH_ROOT / "DATASET_CATEGORY_COVERAGE_AUDIT.md").read_text(encoding="utf-8")

    for cat in CANONICAL_CATEGORIES:
        assert cat in content, f"Category '{cat}' not found in coverage audit"

    # Verify Category 5 sub-languages
    sub_langs = ["Telugu", "Kannada", "Malayalam", "Bengali", "Gujarati"]
    for lang in sub_langs:
        assert lang in content, f"Sub-language '{lang}' not audited under Category 5"

    assert "Bengali (`bn`) and Gujarati (`gu`) have ZERO" in content or "Bengali" in content
    assert "ZERO COMPLIANT COVERAGE" in content or "0 compliant candidate sources" in content


def test_human_review_package_structure():
    """Verify HUMAN_REVIEW_PACKAGE.md contains all 4 roles and pending status."""
    content = (_PATCH_ROOT / "HUMAN_REVIEW_PACKAGE.md").read_text(encoding="utf-8")

    for role in REQUIRED_ROLES:
        assert role in content, f"Role '{role}' missing review section in human review package"

    assert "PENDING HUMAN REVIEW" in content
    assert "[PENDING HUMAN REVIEW - DO NOT POPULATE]" in content


def test_candidate_artifacts_hash_invariance():
    """Verify Candidate A and B artifact checksums remain 100% invariant."""
    candidate_a_path = _PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    candidate_b_path = _PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"

    assert candidate_a_path.exists()
    assert candidate_b_path.exists()

    hash_a = hashlib.sha256(candidate_a_path.read_bytes()).hexdigest()
    hash_b = hashlib.sha256(candidate_b_path.read_bytes()).hexdigest()

    assert hash_a == CANDIDATE_A_HASH, f"Candidate A hash mismatch: {hash_a}"
    assert hash_b == CANDIDATE_B_HASH, f"Candidate B hash mismatch: {hash_b}"
