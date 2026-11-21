#!/usr/bin/env python3
"""IGRIS 3B.51.23.14 — fail-closed derivative cleanup workflow preflight.

This version is intentionally PREVIEW ONLY. It never edits the source corpus,
never writes a cleaned corpus, and refuses to proceed if any proposed row lacks
explicit license clearance and separate cleanup authorization.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, pathlib, sys

REQUIRED = {"source_line", "proposed_gate", "license_clearance", "cleanup_authorization", "notes"}
ALLOWED = {"APPROVED", "PENDING", "REJECTED"}

def sha256(path: pathlib.Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""): h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--clean", required=True, help="Path to existing clean corpus; read-only")
    ap.add_argument("--manifest", default=str(pathlib.Path(__file__).resolve().parents[1]/"metadata"/"derivative_cleanup_gate_manifest.csv"))
    ap.add_argument("--out", default="reports/cleanup_preflight")
    args=ap.parse_args()
    clean=pathlib.Path(args.clean)
    manifest=pathlib.Path(args.manifest)
    out=pathlib.Path(args.out); out.mkdir(parents=True,exist_ok=True)
    errors=[]
    if not clean.is_file(): errors.append("clean corpus not found")
    if not manifest.is_file(): errors.append("gate manifest not found")
    rows=[]
    if not errors:
        with manifest.open("r",encoding="utf-8-sig",newline="") as f:
            reader=csv.DictReader(f)
            if not REQUIRED.issubset(set(reader.fieldnames or [])): errors.append("manifest columns missing")
            else:
                for row in reader:
                    try: line=int(row["source_line"])
                    except Exception: errors.append("invalid source_line"); continue
                    if line<1: errors.append(f"invalid source line {line}")
                    if row["license_clearance"] not in ALLOWED: errors.append(f"invalid license status at line {line}")
                    if row["cleanup_authorization"] not in ALLOWED: errors.append(f"invalid cleanup status at line {line}")
                    rows.append(row)
    source_hash=sha256(clean) if clean.is_file() else None
    line_count=sum(1 for _ in clean.open("r",encoding="utf-8")) if clean.is_file() else None
    blockers=[r["source_line"] for r in rows if r["license_clearance"]!="APPROVED" or r["cleanup_authorization"]!="APPROVED"]
    report={
      "milestone":"3B.51.23.14","status":"PREFLIGHT_BLOCKED_PENDING_GATES" if blockers or errors else "PREFLIGHT_GATES_SATISFIED_REVIEW_REQUIRED",
      "records_in_manifest":len(rows),"blocked_records":len(blockers),"blocked_source_lines":blockers,
      "errors":errors,"source_sha256":source_hash,"source_line_count":line_count,
      "source_modified":False,"derivative_created":False,"cleanup_executed":False,
      "license_clearance_required_for_each_record":True,
      "separate_cleanup_authorization_required_for_each_record":True,
      "decision":"PREVIEW_ONLY_NO_OUTPUT_CORPUS_CREATED"
    }
    (out/"cleanup_preflight_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 2 if errors else 0
if __name__=="__main__": raise SystemExit(main())
