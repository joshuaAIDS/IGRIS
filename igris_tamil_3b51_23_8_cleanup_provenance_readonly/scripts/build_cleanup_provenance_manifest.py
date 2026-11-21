#!/usr/bin/env python3
"""Read-only cleanup/provenance manifest builder for IGRIS Tamil corpus.

Reads the clean corpus and the approved 42-row register. Does not alter source
corpus/register, remove records, normalize text, or promote records.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re
from pathlib import Path

EXPECTED_CLEAN_SHA = "8b26af54e5b77c1434d583b487cec4db8af6a2560bdfdff015e85d8e8ea45064"
EXPECTED_REGISTER_ROWS = 42
EXPECTED_KEEP = 20
EXPECTED_QUARANTINE = 22
APPROVED = {"APPROVED_CLASSIFICATION_ONLY", "APPROVED"}

def digest(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description="Build read-only Tamil cleanup and provenance review manifest.")
    ap.add_argument("--clean",required=True)
    ap.add_argument("--register",required=True)
    ap.add_argument("--out",default="reports/cleanup_provenance_review")
    a=ap.parse_args()
    clean,reg,out=Path(a.clean),Path(a.register),Path(a.out)
    out.mkdir(parents=True,exist_ok=True)
    errors=[]
    ch=digest(clean)
    if ch!=EXPECTED_CLEAN_SHA: errors.append(f"Clean corpus hash mismatch: {ch}")
    raw=clean.read_bytes()
    try: lines=raw.decode("utf-8",errors="strict").splitlines()
    except UnicodeDecodeError as e:
        lines=[]; errors.append(f"Clean corpus UTF-8 error: {e}")
    with reg.open("r",encoding="utf-8-sig",newline="") as f:
        rd=csv.DictReader(f)
        required={"source_line","recommended_classification","manual_review_rationale","human_approval_status"}
        missing=required-set(rd.fieldnames or [])
        if missing: errors.append("Missing register columns: "+",".join(sorted(missing)))
        rows=list(rd)
    if len(rows)!=EXPECTED_REGISTER_ROWS: errors.append(f"Expected 42 register rows, got {len(rows)}")
    keep=[]; quarantine=0; seen=set()
    for r in rows:
        try: n=int(r["source_line"])
        except Exception:
            errors.append(f"Bad source line: {r.get('source_line')}"); continue
        if n in seen: errors.append(f"Duplicate register source line {n}")
        seen.add(n)
        cls=(r.get("recommended_classification") or "").strip()
        approval=(r.get("human_approval_status") or "").strip()
        if approval not in APPROVED: errors.append(f"Line {n} approval status not approved: {approval}")
        if cls=="QUARANTINE_REVIEW": quarantine+=1
        elif cls=="KEEP_WITH_CLEANUP_REVIEW":
            if n<1 or n>len(lines): errors.append(f"Line {n} outside corpus bounds"); continue
            keep.append((n,r,lines[n-1]))
        else: errors.append(f"Line {n} invalid classification {cls}")

    if len(keep)!=EXPECTED_KEEP: errors.append(f"Expected 20 keep candidates, got {len(keep)}")
    if quarantine!=EXPECTED_QUARANTINE: errors.append(f"Expected 22 quarantine rows, got {quarantine}")

    items=[]
    for n,r,text in sorted(keep,key=lambda x:x[0]):
        checks=[]
        if re.search(r"https?://|www\.",text,re.I): checks.append("URL_OR_WEB_REFERENCE")
        if re.search(r"<[^>]{1,80}>|&(?:nbsp|amp|lt|gt);",text,re.I): checks.append("HTML_OR_ENTITY_MARKUP")
        if re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",text): checks.append("EMAIL_ADDRESS_POSSIBLE")
        if re.search(r"\b(?:\+?\d[\d -]{7,}\d)\b",text): checks.append("PHONE_NUMBER_POSSIBLE")
        if "\u00a0" in text: checks.append("NBSP_WHITESPACE")
        if re.search(r" {2,}|\t",text): checks.append("REPEATED_OR_TAB_WHITESPACE")
        if re.search(r"(?:Previous Post|Next Post|Tags:|Read more|Advertisement)",text,re.I): checks.append("WEB_NAV_OR_AD_MARKER")
        rationale=(r.get("manual_review_rationale") or "").strip()
        items.append({
            "source_line":n,
            "classification":"KEEP_WITH_CLEANUP_REVIEW",
            "approval_status":r.get("human_approval_status"),
            "stage3_flag_reason":r.get("stage3_flag_reason",""),
            "manual_review_rationale":rationale,
            "record_characters":len(text),
            "record_sha256_utf8":hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "automated_review_flags":checks,
            "cleanup_action":"MANUAL_DECISION_REQUIRED; no automatic cleanup applied",
            "provenance_status":"UNVERIFIED_FROM_TEXT_FILE",
            "privacy_status":"MANUAL_REVIEW_REQUIRED" if any(x in checks for x in ["EMAIL_ADDRESS_POSSIBLE","PHONE_NUMBER_POSSIBLE"]) or re.search(r"email|phone|contact|address|aadhaar|pan",rationale,re.I) else "NOT_ASSESSED",
            "source_url_or_publication":"NOT_PRESENT_IN_APPROVED_REGISTER",
            "license_and_rights":"NOT_VERIFIED",
            "training_eligibility":"NOT_APPROVED"
        })
    status="PASS_READ_ONLY_MANIFEST" if not errors else "FAIL_REVIEW_REQUIRED"
    report={
        "status":status,
        "audit_type":"READ_ONLY_CLEANUP_AND_PROVENANCE_REVIEW_MANIFEST",
        "clean_corpus_sha256":ch,
        "clean_corpus_line_count":len(lines),
        "approved_register_rows":len(rows),
        "keep_candidates_manifested":len(items),
        "quarantine_rows_count":quarantine,
        "errors":errors,
        "decision":"20_KEEP_CANDIDATES_READY_FOR_MANUAL_CLEANUP_AND_PROVENANCE_REVIEW_ONLY; 22_QUARANTINE_ROWS_STAY_EXCLUDED; NO_SOURCE_CHANGES; NO_TRAINING" if not errors else "STOP_AND_RESOLVE_ERRORS",
        "limitations":[
            "Text heuristics are flags, not proof of contamination or privacy exposure.",
            "Source provenance, original publication, author rights, and license cannot be established from this cleaned text file alone.",
            "No text has been cleaned, redacted, deleted, merged, or promoted.",
            "The 20 rows are not yet approved for tokenizer training."
        ]
    }
    (out/"cleanup_provenance_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"cleanup_provenance_manifest.json").write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding="utf-8")
    fields=["source_line","classification","approval_status","stage3_flag_reason","manual_review_rationale","record_characters","record_sha256_utf8","automated_review_flags","cleanup_action","provenance_status","privacy_status","source_url_or_publication","license_and_rights","training_eligibility"]
    with (out/"cleanup_provenance_manifest.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for x in items:
            y=x.copy(); y["automated_review_flags"]=";".join(y["automated_review_flags"])
            w.writerow(y)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if not errors else 2

if __name__=="__main__": raise SystemExit(main())
