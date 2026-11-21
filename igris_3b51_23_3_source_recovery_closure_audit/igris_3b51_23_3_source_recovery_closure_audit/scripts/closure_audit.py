#!/usr/bin/env python3
"""Read-only source recovery closure audit; emits separate review-only candidates."""
from __future__ import annotations
import argparse
import hashlib
import json
import unicodedata
from pathlib import Path

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def nested(obj, keys, default=None):
    cur = obj
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur

def load_jsonl(path: Path):
    out = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if line.strip():
                out.append((line_no, json.loads(line)))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--unresolved", required=True)
    ap.add_argument("--recovery-report", required=True)
    ap.add_argument("--deep-report", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    raw_path = Path(args.raw)
    unresolved_path = Path(args.unresolved)
    recovery_path = Path(args.recovery_report)
    deep_path = Path(args.deep_report)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    recovery = json.loads(recovery_path.read_text(encoding="utf-8"))
    deep = json.loads(deep_path.read_text(encoding="utf-8"))

    raw_hash = sha256_file(raw_path)
    expected_hash = recovery.get("raw_source_sha256")
    if not expected_hash:
        raise SystemExit("BLOCKED: recovery report missing raw_source_sha256.")
    if raw_hash.lower() != str(expected_hash).lower():
        raise SystemExit("BLOCKED: raw source SHA-256 does not match recovery report.")

    deep_hash = deep.get("raw_source_sha256")
    if deep_hash and raw_hash.lower() != str(deep_hash).lower():
        raise SystemExit("BLOCKED: raw source SHA-256 does not match deep investigation report.")
    if deep.get("decision") != "DIAGNOSTIC_ONLY_NO_RECORDS_APPROVED":
        raise SystemExit("BLOCKED: deep investigation report decision is unexpected.")

    # Strict UTF-8 decode; splitlines removes line terminators, not content spaces.
    raw_lines = raw_path.read_text(encoding="utf-8", errors="strict").splitlines()
    inputs = load_jsonl(unresolved_path)
    deep_cases = deep.get("cases", [])
    deep_by_line = {
        c.get("source_line_1_based"): c
        for c in deep_cases if isinstance(c, dict)
    }

    seen_lines = set()
    audit_cases = []
    review_records = []
    blockers = []
    for index, (jsonl_line, record) in enumerate(inputs, 1):
        line_no = record.get("source_line_1_based")
        preview = nested(record, ("original_classification_record", "original_record", "text"))
        truncated = bool(record.get("truncated_flag"))
        case = {
            "case": index,
            "unresolved_jsonl_line": jsonl_line,
            "source_line_1_based": line_no,
            "truncated_flag": truncated,
            "original_recovery_status": record.get("recovery_status"),
        }

        if not isinstance(line_no, int) or not (1 <= line_no <= len(raw_lines)):
            case.update({"closure_check": "BLOCKED_INVALID_SOURCE_LINE"})
            blockers.append(f"invalid source line reference at unresolved JSONL line {jsonl_line}")
            audit_cases.append(case)
            continue
        if line_no in seen_lines:
            case.update({"closure_check": "BLOCKED_DUPLICATE_SOURCE_LINE"})
            blockers.append(f"duplicate source line reference: {line_no}")
            audit_cases.append(case)
            continue
        seen_lines.add(line_no)

        source_text = raw_lines[line_no - 1]
        if not isinstance(preview, str):
            case.update({"closure_check": "BLOCKED_MISSING_PREVIEW"})
            blockers.append(f"missing preview at unresolved JSONL line {jsonl_line}")
            audit_cases.append(case)
            continue

        n_preview = unicodedata.normalize("NFC", preview)
        n_source = unicodedata.normalize("NFC", source_text)
        if truncated:
            matched = n_source.startswith(n_preview)
            match_type = "NFC_PREFIX_MATCH" if matched else "NO_MATCH"
        else:
            matched = n_preview == n_source
            match_type = "NFC_EXACT_MATCH" if matched else "NO_MATCH"

        deep_case = deep_by_line.get(line_no)
        deep_comparison = deep_case.get("comparison") if deep_case else None
        deep_consistent = (
            deep_comparison == "TRUNCATED_NFC_PREFIX_MATCH" if truncated
            else deep_comparison == "NFC_MATCH"
        )
        case.update({
            "closure_check": "SOURCE_CORRESPONDENCE_CONFIRMED" if matched and deep_consistent else "REVIEW_REQUIRED",
            "match_type_recomputed": match_type,
            "deep_report_comparison": deep_comparison,
            "deep_report_consistent": deep_consistent,
            "preview_chars": len(preview),
            "source_line_chars": len(source_text),
            "source_line_sha256_utf8": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
            "preview_sha256_utf8": hashlib.sha256(preview.encode("utf-8")).hexdigest(),
        })
        audit_cases.append(case)

        if matched and deep_consistent:
            review_records.append({
                "review_only": True,
                "approval_status": "NOT_APPROVED",
                "recovery_source": "raw_source_line",
                "source_line_1_based": line_no,
                "original_unresolved_jsonl_line": jsonl_line,
                "original_record_preserved": record,
                "recovered_full_source_text": source_text,
                "source_line_sha256_utf8": case["source_line_sha256_utf8"],
                "note": "Full source line copied to a separate review artifact; not merged into corpus."
            })
        else:
            blockers.append(f"source/deep-report correspondence not confirmed for source line {line_no}")

    # Require the expected ten cases and ten confirmed cases for closure.
    confirmed = sum(1 for c in audit_cases if c.get("closure_check") == "SOURCE_CORRESPONDENCE_CONFIRMED")
    if len(inputs) != 10:
        blockers.append(f"expected 10 unresolved records, found {len(inputs)}")
    if confirmed != len(inputs):
        blockers.append(f"confirmed {confirmed} of {len(inputs)} unresolved records")

    report = {
        "status": "PASS_WITH_REVIEW" if not blockers else "BLOCKED",
        "raw_source_sha256": raw_hash,
        "raw_source_hash_matches_recovery_report": True,
        "raw_source_hash_matches_deep_report": (not deep_hash or raw_hash.lower() == str(deep_hash).lower()),
        "raw_source_line_count": len(raw_lines),
        "unresolved_records_checked": len(inputs),
        "source_correspondence_confirmed": confirmed,
        "review_only_candidate_records_written": len(review_records),
        "blockers": blockers,
        "cases": audit_cases,
        "decision": "SOURCE_CORRESPONDENCE_CONFIRMED_REVIEW_ONLY_NOT_DATASET_APPROVAL" if not blockers else "NO_CLOSURE_BLOCKED",
        "notes": [
            "All inputs were read-only; no source or recovery inputs were modified.",
            "Full source lines are written only to a separate review-only JSONL.",
            "Original unresolved metadata is preserved inside each review record.",
            "No record is approved for training or corpus inclusion.",
            "Content quality, source provenance, licensing, and commercial rights remain separate review gates."
        ]
    }
    (out_dir / "source_recovery_closure_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with (out_dir / "recovered_source_lines_review_only.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for item in review_records:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(json.dumps({
        "status": report["status"],
        "unresolved_records_checked": len(inputs),
        "source_correspondence_confirmed": confirmed,
        "review_only_candidate_records_written": len(review_records),
        "blockers": blockers,
        "outputs": [
            str(out_dir / "source_recovery_closure_report.json"),
            str(out_dir / "recovered_source_lines_review_only.jsonl")
        ],
        "decision": report["decision"]
    }, ensure_ascii=False, indent=2))
    if blockers:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
