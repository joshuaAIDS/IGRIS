"""
Unit tests for Milestone 3C.5: Human Review & Dataset Gap Resolution Planning.
Validates the four role review documents, decision register, gap research reports,
resolution plan, and candidate artifact invariance.
"""

import csv
import hashlib
from pathlib import Path
import pytest

_PATCH_ROOT = Path(__file__).resolve().parent.parent

CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

PRIMARY_DELIVERABLES = [
    "IGRIS_3C5_HUMAN_REVIEW_PLAN.md",
    "DATASET_REVIEW_DECISION_REGISTER.csv",
    "BENGALI_GUJARATI_SOURCE_RESEARCH.md",
    "CONVERSATIONAL_DATASET_RESEARCH.md",
    "DATASET_GAP_RESOLUTION_PLAN.md",
    "IGRIS_3C5_STATUS.md",
]

ROLE_DOCUMENTS = [
    ("REVIEW_DATA_CUSTODIAN.md", "DATA_CUSTODIAN"),
    ("REVIEW_LEGAL_GOVERNANCE.md", "LEGAL_GOVERNANCE"),
    ("REVIEW_SECURITY_PRIVACY.md", "SECURITY_PRIVACY"),
    ("REVIEW_CHIEF_ARCHITECT.md", "CHIEF_ARCHITECT"),
]


def test_3c5_deliverables_exist():
    """Verify all primary Milestone 3C.5 deliverables exist."""
    for filename in PRIMARY_DELIVERABLES:
        path = _PATCH_ROOT / filename
        assert path.exists(), f"Missing primary 3C.5 deliverable: {filename}"
        assert path.stat().st_size > 500, f"Deliverable {filename} is suspiciously small"


def test_3c5_role_review_documents_exist_and_pending():
    """Verify all 4 dedicated role review documents exist, cover 26 sources, and are pending."""
    for filename, role_name in ROLE_DOCUMENTS:
        path = _PATCH_ROOT / filename
        assert path.exists(), f"Missing role review document: {filename}"
        content = path.read_text(encoding="utf-8")
        assert role_name in content, f"Role '{role_name}' not mentioned in {filename}"
        assert "PENDING HUMAN REVIEW" in content
        assert "SRC-TM-01" in content
        assert "SRC-EM-02" in content


def test_dataset_review_decision_register_schema_and_counts():
    """Verify DATASET_REVIEW_DECISION_REGISTER.csv has 26 sources, required columns, and correct counts."""
    csv_path = _PATCH_ROOT / "DATASET_REVIEW_DECISION_REGISTER.csv"
    assert csv_path.exists()

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 26, f"Expected 26 sources, found {len(rows)}"

    expected_cols = {
        "source_id",
        "dataset_name",
        "canonical_category",
        "exact_license",
        "technical_verification_status",
        "data_custodian_recommendation",
        "legal_governance_recommendation",
        "security_privacy_recommendation",
        "chief_architect_recommendation",
        "consensus_classification",
        "distinction_notes",
        "human_review_status",
    }
    assert expected_cols.issubset(set(reader.fieldnames or []))

    counts = {"VERIFIED": 0, "REQUIRES HUMAN APPROVAL": 0, "INCOMPATIBLE": 0, "UNVERIFIED": 0}
    for row in rows:
        cls = row["consensus_classification"]
        assert cls in counts, f"Invalid consensus classification '{cls}' in row {row['source_id']}"
        counts[cls] += 1
        assert row["human_review_status"] == "PENDING"

    assert counts["VERIFIED"] == 14
    assert counts["REQUIRES HUMAN APPROVAL"] == 7
    assert counts["INCOMPATIBLE"] == 4
    assert counts["UNVERIFIED"] == 1


def test_bengali_gujarati_research_content():
    """Verify BENGALI_GUJARATI_SOURCE_RESEARCH.md covers Bengali and Gujarati under CC0."""
    content = (_PATCH_ROOT / "BENGALI_GUJARATI_SOURCE_RESEARCH.md").read_text(encoding="utf-8")
    assert "Bengali" in content
    assert "Gujarati" in content
    assert "IndicCorp v2" in content
    assert "CC0-1.0" in content
    assert "SRC-OI-04" in content
    assert "SRC-OI-05" in content


def test_conversational_research_content():
    """Verify CONVERSATIONAL_DATASET_RESEARCH.md rejects NC/scraped data and evaluates compliant sources."""
    content = (_PATCH_ROOT / "CONVERSATIONAL_DATASET_RESEARCH.md").read_text(encoding="utf-8")
    assert "DailyDialog" in content
    assert "OpenSubtitles" in content
    assert "OpenAssistant" in content
    assert "Anthropic" in content
    assert "Apache-2.0" in content
    assert "MIT" in content
    assert "Public Domain" in content


def test_dataset_gap_resolution_plan_content():
    """Verify DATASET_GAP_RESOLUTION_PLAN.md covers all 10 categories and the 4-stage protocol."""
    content = (_PATCH_ROOT / "DATASET_GAP_RESOLUTION_PLAN.md").read_text(encoding="utf-8")
    assert "Four-Stage Gap Resolution Protocol" in content or "Four-Stage Resolution Protocol" in content
    assert "Category 5 Gap" in content
    assert "Category 9 Deficit" in content
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
