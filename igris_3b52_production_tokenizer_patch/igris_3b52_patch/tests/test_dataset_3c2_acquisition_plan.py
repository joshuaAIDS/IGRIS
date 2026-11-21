"""Tests for IGRIS Milestone 3C.2 — Dataset Acquisition Planning.

Verifies:
- All 10 categories are covered in DATASET_SOURCE_CATALOG.csv.
- Every source has published URL, license, owner, and estimated size.
- All human_approval_status fields require human approval.
- All verification statuses are VERIFIED or UNVERIFIED.
- Milestone 3C.2 planning deliverables exist and conform to governance standards.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
import pytest

# Add patch src and scripts
_PATCH_ROOT = Path(__file__).resolve().parents[1]
_PATCH_SRC = str(_PATCH_ROOT / "src")
_PATCH_SCRIPTS = str(_PATCH_ROOT / "scripts")
for p in [_PATCH_SRC, _PATCH_SCRIPTS]:
    if p not in sys.path:
        sys.path.insert(0, p)

from dataset_inventory import APPROVED_CATEGORIES

CATALOG_PATH = _PATCH_ROOT / "DATASET_SOURCE_CATALOG.csv"
LICENSE_COMP_PATH = _PATCH_ROOT / "DATASET_LICENSE_COMPARISON.md"
RISK_REG_PATH = _PATCH_ROOT / "DATASET_ACQUISITION_RISK_REGISTER.md"
PLAN_PATH = _PATCH_ROOT / "IGRIS_3C2_ACQUISITION_PLAN.md"
STATUS_PATH = _PATCH_ROOT / "IGRIS_3C2_STATUS.md"


class TestMilestone3C2AcquisitionPlan:
    """Test suite for Milestone 3C.2 Dataset Acquisition Planning."""

    def test_catalog_exists_and_covers_all_10_categories(self):
        assert CATALOG_PATH.is_file(), f"Missing {CATALOG_PATH}"
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))

        assert len(reader) >= 20, f"Expected at least 20 candidate sources, found {len(reader)}"
        catalog_cats = {r["category"] for r in reader}
        missing_cats = set(APPROVED_CATEGORIES) - catalog_cats
        assert missing_cats == set(), f"Missing categories in catalog: {missing_cats}"

    def test_catalog_field_validity_and_urls(self):
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))

        for r in reader:
            assert r["source_id"].startswith("SRC-")
            assert len(r["dataset_name"]) > 0
            assert r["official_source_url"].startswith("http")
            assert len(r["published_license"]) > 0
            assert len(r["dataset_owner_org"]) > 0
            assert len(r["published_size_estimate"]) > 0
            assert r["verification_status"] in ("VERIFIED", "UNVERIFIED")
            assert r["human_approval_status"] == "REQUIRES HUMAN APPROVAL"

    def test_all_deliverable_documents_exist_and_non_empty(self):
        for p, name in [
            (LICENSE_COMP_PATH, "DATASET_LICENSE_COMPARISON.md"),
            (RISK_REG_PATH, "DATASET_ACQUISITION_RISK_REGISTER.md"),
            (PLAN_PATH, "IGRIS_3C2_ACQUISITION_PLAN.md"),
            (STATUS_PATH, "IGRIS_3C2_STATUS.md"),
        ]:
            assert p.is_file(), f"Missing document {name}"
            assert p.stat().st_size > 500, f"Document {name} is suspiciously small"

    def test_status_document_classifications(self):
        content = STATUS_PATH.read_text(encoding="utf-8")
        assert "VERIFIED" in content
        assert "UNVERIFIED" in content
        assert "REQUIRES HUMAN APPROVAL" in content
        assert "NOT AVAILABLE" in content
        assert "PRODUCTION ACCESS LOCKED" in content
