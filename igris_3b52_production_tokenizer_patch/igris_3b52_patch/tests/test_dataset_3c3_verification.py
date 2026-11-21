"""
Unit tests for Milestone 3C.3: Dataset Source and License Verification.
Verifies approval role reconciliation, category reconciliation, license audit CSV,
risk updates, and governance invariants.
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


def test_3c3_deliverables_exist():
    """Verify all five Milestone 3C.3 deliverables exist."""
    required_files = [
        "APPROVAL_ROLE_RECONCILIATION.md",
        "DATASET_CATEGORY_RECONCILIATION.md",
        "DATASET_LICENSE_AUDIT.csv",
        "DATASET_SOURCE_RISK_UPDATE.md",
        "IGRIS_3C3_SOURCE_VERIFICATION_REPORT.md",
    ]
    for filename in required_files:
        path = _PATCH_ROOT / filename
        assert path.exists(), f"Missing required Milestone 3C.3 deliverable: {filename}"
        assert path.stat().st_size > 500, f"Deliverable {filename} is suspiciously small"


def test_approval_role_reconciliation_content():
    """Verify role reconciliation documents the four original roles and two proposed roles."""
    content = (_PATCH_ROOT / "APPROVAL_ROLE_RECONCILIATION.md").read_text(encoding="utf-8")
    original_roles = ["DATA_CUSTODIAN", "LEGAL_GOVERNANCE", "SECURITY_PRIVACY", "CHIEF_ARCHITECT"]
    proposed_roles = ["AI_ETHICS_SAFETY", "TECHNICAL_LEAD"]

    for role in original_roles:
        assert role in content, f"Original role '{role}' not documented in reconciliation"

    for role in proposed_roles:
        assert role in content, f"Proposed role '{role}' not documented in reconciliation"

    assert "Do not silently replace" in content or "not silently replace" in content


def test_category_reconciliation_content():
    """Verify category reconciliation covers all 10 canonical categories and identifies discrepancies."""
    content = (_PATCH_ROOT / "DATASET_CATEGORY_RECONCILIATION.md").read_text(encoding="utf-8")
    for category in CANONICAL_CATEGORIES:
        assert category in content, f"Canonical category '{category}' not found in reconciliation"

    assert "DATASET_SPECIFICATION.md" in content
    assert "DATASET_SOURCE_CATALOG.csv" in content


def test_dataset_license_audit_csv_schema_and_counts():
    """Verify DATASET_LICENSE_AUDIT.csv covers exactly 26 sources with valid fields and classifications."""
    csv_path = _PATCH_ROOT / "DATASET_LICENSE_AUDIT.csv"
    assert csv_path.exists()

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 26, f"Expected 26 sources, found {len(rows)}"

    valid_classifications = {"VERIFIED", "UNVERIFIED", "INCOMPATIBLE", "REQUIRES HUMAN APPROVAL"}
    counts = {c: 0 for c in valid_classifications}

    for row in rows:
        assert row["source_id"].startswith("SRC-")
        assert row["audit_classification"] in valid_classifications, (
            f"Invalid classification '{row['audit_classification']}' for {row['source_id']}"
        )
        counts[row["audit_classification"]] += 1
        assert row["official_source_url"].startswith("http")
        assert len(row["exact_license"]) > 0
        assert row["canonical_category"] in CANONICAL_CATEGORIES, (
            f"Category '{row['canonical_category']}' not in canonical 10 categories"
        )

    assert counts["VERIFIED"] == 14, f"Expected 14 VERIFIED sources, got {counts['VERIFIED']}"
    assert counts["UNVERIFIED"] == 1, f"Expected 1 UNVERIFIED source, got {counts['UNVERIFIED']}"
    assert counts["INCOMPATIBLE"] == 4, f"Expected 4 INCOMPATIBLE sources, got {counts['INCOMPATIBLE']}"
    assert counts["REQUIRES HUMAN APPROVAL"] == 7, (
        f"Expected 7 REQUIRES HUMAN APPROVAL sources, got {counts['REQUIRES HUMAN APPROVAL']}"
    )


def test_candidate_artifacts_hash_invariance():
    """Verify Candidate A and B artifact checksums remain perfectly invariant."""
    candidate_a_path = _PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    candidate_b_path = _PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"

    assert candidate_a_path.exists()
    assert candidate_b_path.exists()

    hash_a = hashlib.sha256(candidate_a_path.read_bytes()).hexdigest()
    hash_b = hashlib.sha256(candidate_b_path.read_bytes()).hexdigest()

    assert hash_a == CANDIDATE_A_HASH, f"Candidate A hash changed: {hash_a}"
    assert hash_b == CANDIDATE_B_HASH, f"Candidate B hash changed: {hash_b}"
