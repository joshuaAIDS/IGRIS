"""
Unit tests for Milestone 3C.6: Dataset Source Validation & Governance Review Freeze.
Validates the V2 source catalog, conversational data classification, source ID integrity,
governance freeze orders, and candidate artifact invariance.
"""

import csv
import hashlib
from pathlib import Path
import pytest

_PATCH_ROOT = Path(__file__).resolve().parent.parent

CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

DELIVERABLES = [
    "IGRIS_3C6_VALIDATION_REPORT.md",
    "DATASET_SOURCE_CATALOG_V2.csv",
    "CONVERSATIONAL_DATA_CLASSIFICATION.md",
    "SOURCE_ID_INTEGRITY_REPORT.md",
    "DATASET_GOVERNANCE_FREEZE.md",
    "IGRIS_3C6_STATUS.md",
]

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


def test_3c6_deliverables_exist():
    """Verify all Milestone 3C.6 deliverables exist and have content."""
    for filename in DELIVERABLES:
        path = _PATCH_ROOT / filename
        assert path.exists(), f"Missing 3C.6 deliverable: {filename}"
        assert path.stat().st_size > 500, f"Deliverable {filename} is suspiciously small"


def test_catalog_v2_schema_and_counts():
    """Verify DATASET_SOURCE_CATALOG_V2.csv covers exactly 32 sources with all required fields."""
    csv_path = _PATCH_ROOT / "DATASET_SOURCE_CATALOG_V2.csv"
    assert csv_path.exists()

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 32, f"Expected 32 sources in V2 catalog, found {len(rows)}"

    expected_cols = {
        "source_id",
        "dataset_name",
        "category",
        "primary_language",
        "script",
        "dataset_owner_org",
        "official_source_url",
        "published_license",
        "commercial_use_allowed",
        "evaluation_use_allowed",
        "published_size_estimate",
        "provenance_type",
        "pii_risk_level",
        "verification_status",
        "human_approval_status",
        "notes",
    }
    assert expected_cols.issubset(set(reader.fieldnames or []))

    # Verify ID continuity and new sources
    source_ids = {r["source_id"] for r in rows}
    assert "SRC-OI-04" in source_ids
    assert "SRC-OI-05" in source_ids
    assert "SRC-CV-03" in source_ids
    assert "SRC-CV-04" in source_ids
    assert "SRC-CV-05" in source_ids
    assert "SRC-CV-06" in source_ids

    # Verify all 10 categories are present
    categories = {r["category"] for r in rows}
    for cat in CANONICAL_CATEGORIES:
        assert cat in categories, f"Category '{cat}' missing from V2 catalog"


def test_conversational_classification_subtypes():
    """Verify CONVERSATIONAL_DATA_CLASSIFICATION.md covers all 5 subtypes and pipeline boundaries."""
    content = (_PATCH_ROOT / "CONVERSATIONAL_DATA_CLASSIFICATION.md").read_text(encoding="utf-8")

    subtypes = ["Subtype A", "Subtype B", "Subtype C", "Subtype D", "Subtype E"]
    for st in subtypes:
        assert st in content, f"Subtype '{st}' missing from conversational classification"

    assert "Tokenizer Pre-Training" in content
    assert "Tokenizer Evaluation" in content
    assert "Separate Alignment" in content or "Alignment Evaluation" in content
    assert "ABSOLUTELY BANNED" in content or "strictly prohibited" in content


def test_source_id_integrity_report_content():
    """Verify SOURCE_ID_INTEGRITY_REPORT.md documents SRC-CV-05 and prohibits silent renumbering."""
    content = (_PATCH_ROOT / "SOURCE_ID_INTEGRITY_REPORT.md").read_text(encoding="utf-8")

    assert "SRC-CV-05" in content
    assert "MultiWOZ" in content
    assert "SRC-CV-06" in content
    assert "renumber" in content or "renumbered" in content


def test_dataset_governance_freeze_order():
    """Verify DATASET_GOVERNANCE_FREEZE.md locks all 4 roles, 10 categories, and architecture."""
    content = (_PATCH_ROOT / "DATASET_GOVERNANCE_FREEZE.md").read_text(encoding="utf-8")

    for role in REQUIRED_ROLES:
        assert role in content, f"Role '{role}' missing from governance freeze"

    for cat in CANONICAL_CATEGORIES:
        assert cat in content, f"Category '{cat}' missing from governance freeze"

    assert "32 sources" in content or "32" in content
    assert "LOCKED" in content


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
