"""Tests for IGRIS Milestone 3B.62 — Production Authorization Readiness Audit.

Verifies that the automated audit engine correctly evaluates governance documents,
schema concordance, human roles, artifact checksums, and default-deny enforcement.
"""

from __future__ import annotations

import json
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

from audit_3b62_readiness import (
    audit_governance_documents,
    audit_schema_concordance,
    audit_human_approval_roles,
    audit_tokenizer_artifacts,
    audit_access_control_security,
    run_full_readiness_audit,
    GOVERNANCE_DOCUMENTS,
)


class TestMilestone3B62ReadinessAudit:
    """Test suite for the Milestone 3B.62 Production Readiness Audit."""

    def test_all_governance_documents_present_and_non_empty(self):
        res = audit_governance_documents()
        assert res["overall_status"] == "PASS"
        for doc in GOVERNANCE_DOCUMENTS:
            detail = res["details"][doc]
            assert detail["exists"] is True, f"Document missing: {doc}"
            assert detail["byte_size"] > 100, f"Document too small: {doc}"

    def test_schema_concordance_passes(self):
        res = audit_schema_concordance()
        assert res["status"] == "PASS"
        assert res["inventory_validation_errors"] == []
        assert res["concordance_issues"] == []

    def test_four_required_human_roles_configured(self):
        res = audit_human_approval_roles()
        assert res["status"] == "PASS"
        assert res["missing_roles"] == []
        assert res["all_approved"] is True
        assert res["all_have_valid_signatures"] is True
        assert res["governance_classification"] == "REQUIRES HUMAN APPROVAL"

    def test_tokenizer_artifact_checksums_match_exact_specification(self):
        res = audit_tokenizer_artifacts()
        assert res["status"] == "PASS"
        assert res["candidate_a"]["match"] is True
        assert res["candidate_b"]["match"] is True

    def test_access_control_default_deny_enforced(self):
        res = audit_access_control_security()
        assert res["status"] == "PASS"
        assert res["template_gate_cleared"] is True
        assert res["unauthorized_production_blocked"] is True

    def test_full_readiness_audit_generates_json_summary(self):
        report = run_full_readiness_audit()
        assert report["milestone"] == "3B.62"
        assert report["overall_status"] == "READY_FOR_HUMAN_GOVERNANCE_REVIEW"
        assert report["item_classifications"]["production_dataset_access"] == "REQUIRES HUMAN APPROVAL"
        assert report["item_classifications"]["production_corpus_ingestion"] == "REQUIRES HUMAN APPROVAL"
        assert report["item_classifications"]["production_tokenizer_training"] == "REQUIRES HUMAN APPROVAL"
        assert report["item_classifications"]["default_deny_enforcement"] == "PASS"
