#!/usr/bin/env python3
"""Read-only audit of the user-approved 42-record Tamil review decisions.

This script does NOT edit, delete, merge, normalize, move, or promote corpus rows.
It validates the approved register against the clean corpus and writes audit reports.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, sys
from pathlib import Path

EXPECTED_SHA256 = "8b26af54e5b77c1434d583b487cec4db8af6a2560bdfdff015e85d8e8ea45064"
EXPECTED_TOTAL = 42
EXPECTED_KEEP = 20
EXPECTED_QUARANTINE = 22
ALLOWED = {"KEEP_WITH_CLEANUP_REVIEW", "QUARANTINE_REVIEW"}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(description="Read-only audit for the approved 42-record Tamil review register.")
    ap.add_argument("--clean", required=True, help="Path to tamil_nfc_deduplicated.txt")
    ap.add_argument("--register", required=True, help="Path to the 42-record consolidated CSV register")
    ap.add_argument("--out", default="reports/approval_audit", help="Output directory")
    args = ap.parse_args()

    clean = Path(args.clean)
    reg = Path(args.register)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    errors=[]
    clean_hash=sha256(clean)
    if clean_hash != EXPECTED_SHA256:
        errors.append(f"Clean corpus SHA-256 mismatch: expected {EXPECTED_SHA256}, got {clean_hash}")

    raw=clean.read_bytes()
    try:
        text=raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as e:
        errors.append(f"Clean corpus is not valid UTF-8: {e}")
        text=""
    lines=text.splitlines()

    records=[]
    with reg.open("r", encoding="utf-8-sig", newline="") as f:
        reader=csv.DictReader(f)
        required={"source_line","recommended_classification","human_approval_status"}
        missing=required-set(reader.fieldnames or [])
        if missing:
            errors.append("Register missing required columns: "+", ".join(sorted(missing)))
        for row in reader:
            try:
                n=int(row["source_line"])
            except Exception:
                errors.append(f"Invalid source_line value: {row.get('source_line')!r}")
                continue
            cls=(row.get("recommended_classification") or "").strip()
            approval=(row.get("human_approval_status") or "").strip()
            records.append({"source_line":n,"classification":cls,"approval":approval})

    if len(records)!=EXPECTED_TOTAL:
        errors.append(f"Expected {EXPECTED_TOTAL} register rows, found {len(records)}")
    nums=[r["source_line"] for r in records]
    if len(set(nums))!=len(nums):
        errors.append("Duplicate source_line entries found in register")

    for r in records:
        n=r["source_line"]
        if r["classification"] not in ALLOWED:
            errors.append(f"Line {n}: invalid classification {r['classification']!r}")
        if r["approval"] not in {"APPROVED_CLASSIFICATION_ONLY","APPROVED"}:
            errors.append(f"Line {n}: approval not marked APPROVED_CLASSIFICATION_ONLY (found {r['approval']!r})")
        if n<1 or n>len(lines):
            errors.append(f"Line {n}: source line is outside corpus bounds")
    keep=sum(r["classification"]=="KEEP_WITH_CLEANUP_REVIEW" for r in records)
    quarantine=sum(r["classification"]=="QUARANTINE_REVIEW" for r in records)
    if keep!=EXPECTED_KEEP: errors.append(f"Expected {EXPECTED_KEEP} keep-with-cleanup rows, found {keep}")
    if quarantine!=EXPECTED_QUARANTINE: errors.append(f"Expected {EXPECTED_QUARANTINE} quarantine rows, found {quarantine}")

    # Record only metadata, line numbers and hashes; do not copy corpus text into report.
    result={
        "status":"PASS_READ_ONLY_AUDIT" if not errors else "FAIL_REVIEW_REQUIRED",
        "audit_type":"APPROVAL_AND_SOURCE_INTEGRITY_VALIDATION_ONLY",
        "clean_corpus_path":str(clean.resolve()),
        "clean_corpus_sha256":clean_hash,
        "clean_corpus_line_count":len(lines),
        "register_path":str(reg.resolve()),
        "register_row_count":len(records),
        "approved_classification_count":sum(r["approval"] in {"APPROVED_CLASSIFICATION_ONLY","APPROVED"} for r in records),
        "keep_with_cleanup_review_count":keep,
        "quarantine_review_count":quarantine,
        "source_line_bounds_valid":all(1<=r["source_line"]<=len(lines) for r in records),
        "errors":errors,
        "decision":"CLASSIFICATION_APPROVAL_ONLY_QUARANTINE_ROWS_REMAIN_EXCLUDED_FROM_CLEAN_TRAINING_CANDIDATES_NO_CORPUS_MODIFICATION_NO_TRAINING" if not errors else "DO_NOT_PROCEED_UNTIL_ERRORS_RESOLVED",
        "note":"User approval is interpreted as approval of the review classifications, not approval to train on quarantined records or as dataset/license clearance."
    }
    (out/"approval_readonly_audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    with (out/"approved_line_inventory.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f); w.writerow(["source_line","classification","approval_status","training_candidate_status"])
        for r in sorted(records,key=lambda x:x["source_line"]):
            candidate="CANDIDATE_PENDING_CLEANUP_AND_PROVENANCE" if r["classification"]=="KEEP_WITH_CLEANUP_REVIEW" else "EXCLUDED_QUARANTINE"
            w.writerow([r["source_line"],r["classification"],r["approval"],candidate])
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if not errors else 2

if __name__=="__main__":
    raise SystemExit(main())
