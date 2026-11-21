#!/usr/bin/env python3
"""Generates IGRIS_PRODUCTION_READINESS_MATRIX.csv for Milestone Phase 6."""

import csv
from pathlib import Path

PATCH_DIR = Path(__file__).resolve().parent.parent

with open(PATCH_DIR / "DATASET_SOURCE_CATALOG_V3.csv", "r", encoding="utf-8") as f:
    cat = list(csv.DictReader(f))
with open(PATCH_DIR / "DATASET_LICENSE_CLASSIFICATION_V3.csv", "r", encoding="utf-8") as f:
    lic = {r["source_id"]: r for r in csv.DictReader(f)}
with open(PATCH_DIR / "PIPELINE_AUTHORIZATION_MATRIX_V2.csv", "r", encoding="utf-8") as f:
    pipe = {r["source_id"]: r for r in csv.DictReader(f)}
with open(PATCH_DIR / "SOURCE_APPROVAL_STATE_V2.csv", "r", encoding="utf-8") as f:
    app = {r["source_id"]: r for r in csv.DictReader(f)}

out_path = PATCH_DIR / "IGRIS_PRODUCTION_READINESS_MATRIX.csv"
fieldnames = [
    "source_id",
    "dataset_name",
    "canonical_category",
    "published_license",
    "license_class",
    "technical_verification_status",
    "custodian_readiness",
    "legal_readiness",
    "security_readiness",
    "architect_readiness",
    "production_gate_status",
    "blocking_dependencies",
]

rows = []
for r in cat:
    sid = r["source_id"]
    l_info = lic[sid]
    p_info = pipe[sid]
    a_info = app[sid]

    tech_status = r["license_verification_status"]
    is_rejected = (r["human_approval_status"] == "REJECTED") or (tech_status == "INCOMPATIBLE")

    if is_rejected:
        custodian_readiness = "REJECTED_INCOMPATIBLE"
        legal_readiness = "INCOMPATIBLE_PROHIBITED"
        security_readiness = "REJECTED_INCOMPATIBLE"
        architect_readiness = "INELIGIBLE_REJECTED"
        blocking = "Permanently rejected due to non-commercial clause or unauthorized scraping; Purged from pipeline"
    else:
        custodian_readiness = "READY_PENDING_HUMAN_SIGN_OFF"
        if l_info["license_category"] == "ShareAlike":
            legal_readiness = "REQUIRES_LEGAL_COPYLEFT_RULING"
            blocking = "Pending authentic 4-of-4 sign-off; Requires legal ruling on CC-BY-SA 4.0 adaptation boundary"
        elif l_info["license_category"] == "Public Domain":
            legal_readiness = "REQUIRES_VITAL_DATE_VERIFICATION"
            blocking = "Pending authentic 4-of-4 sign-off; Requires item-level vital date check (Life+60 <= 1965)"
        elif l_info["license_category"] in ["CC0", "Apache-2.0", "MIT"]:
            legal_readiness = "READY_PENDING_HUMAN_SIGN_OFF"
            blocking = "Pending authentic 4-of-4 human review signatures"
        else:
            legal_readiness = "REQUIRES_TERMS_REVIEW"
            notes = r.get("governance_notes", "Pending review")
            blocking = f"Pending authentic 4-of-4 sign-off; {notes}"

        security_readiness = "SCREENING_PROTOCOL_READY_PENDING_REVIEW"
        architect_readiness = p_info["tokenizer_vocab_training"]

    rows.append({
        "source_id": sid,
        "dataset_name": r["dataset_name"],
        "canonical_category": r["category"],
        "published_license": r["published_license"],
        "license_class": l_info["license_category"],
        "technical_verification_status": tech_status,
        "custodian_readiness": custodian_readiness,
        "legal_readiness": legal_readiness,
        "security_readiness": security_readiness,
        "architect_readiness": architect_readiness,
        "production_gate_status": "LOCKED",
        "blocking_dependencies": blocking,
    })

with open(out_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Successfully generated IGRIS_PRODUCTION_READINESS_MATRIX.csv with {len(rows)} rows.")
