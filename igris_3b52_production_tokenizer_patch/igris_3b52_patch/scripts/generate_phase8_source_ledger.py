#!/usr/bin/env python3
"""Generates IGRIS_PHASE8_SOURCE_APPROVAL_LEDGER.csv for Milestone Phase 8."""

import csv
from pathlib import Path

PATCH_DIR = Path(__file__).resolve().parent.parent

with open(PATCH_DIR / "DATASET_SOURCE_CATALOG_V3.csv", "r", encoding="utf-8") as f:
    cat = list(csv.DictReader(f))
with open(PATCH_DIR / "PIPELINE_AUTHORIZATION_MATRIX_V2.csv", "r", encoding="utf-8") as f:
    pipe = {r["source_id"]: r for r in csv.DictReader(f)}

out_path = PATCH_DIR / "IGRIS_PHASE8_SOURCE_APPROVAL_LEDGER.csv"
fieldnames = [
    "source_id",
    "dataset_name",
    "canonical_category",
    "published_license",
    "custodian_submission_status",
    "legal_submission_status",
    "security_submission_status",
    "architect_submission_status",
    "quorum_consensus_status",
    "pipeline_gate_state",
    "permitted_pipeline_scope",
    "rejection_or_block_reason",
]

rows = []
for r in cat:
    sid = r["source_id"]
    p_info = pipe[sid]

    is_catalog_rejected = (r["human_approval_status"] == "REJECTED") or (r["license_verification_status"] == "INCOMPATIBLE")

    if is_catalog_rejected:
        custodian_status = "REJECTED_RECOMMENDED"
        legal_status = "REJECTED_RECOMMENDED"
        security_status = "REJECTED_RECOMMENDED"
        architect_status = "REJECTED_RECOMMENDED"
        quorum_status = "BLOCKED_REJECTED"
        pipeline_gate = "LOCKED"
        permitted_scope = "NONE_UNAUTHORIZED"
        reason = "Permanently blocked due to non-commercial restriction or unauthorized scraping; Purged from pipeline"
    else:
        custodian_status = "AWAITING_AUTHENTIC_SUBMISSION"
        legal_status = "AWAITING_AUTHENTIC_SUBMISSION"
        security_status = "AWAITING_AUTHENTIC_SUBMISSION"
        architect_status = "AWAITING_AUTHENTIC_SUBMISSION"
        quorum_status = "PENDING"
        pipeline_gate = "LOCKED"
        permitted_scope = "NONE_UNAUTHORIZED"
        reason = "Awaiting physical reviewer appointments and authentic cryptographic sign-offs from all 4 roles"

    rows.append({
        "source_id": sid,
        "dataset_name": r["dataset_name"],
        "canonical_category": r["category"],
        "published_license": r["published_license"],
        "custodian_submission_status": custodian_status,
        "legal_submission_status": legal_status,
        "security_submission_status": security_status,
        "architect_submission_status": architect_status,
        "quorum_consensus_status": quorum_status,
        "pipeline_gate_state": pipeline_gate,
        "permitted_pipeline_scope": permitted_scope,
        "rejection_or_block_reason": reason,
    })

with open(out_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Successfully generated IGRIS_PHASE8_SOURCE_APPROVAL_LEDGER.csv with {len(rows)} rows.")
