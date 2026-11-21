#!/usr/bin/env python3
"""Recover full records for flagged mixed-script entries from immutable raw pilot.

This is a read-only source-recovery audit:
- never modifies source files
- never normalizes, deduplicates, or trains
- uses original_record.line as a 1-based line number in the raw source
- checks recovered text against the available preview
- preserves every input classification record in an audit JSONL
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from collections import Counter

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def read_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, raw in enumerate(f, 1):
            if not raw.strip():
                continue
            try:
                rows.append((line_no, json.loads(raw)))
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}: malformed JSON at JSONL line {line_no}: {e}")
    return rows

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", required=True, help="Immutable original 10k-record raw TXT file")
    ap.add_argument("--likely", required=True, help="likely_valid.jsonl")
    ap.add_argument("--contamination", required=True, help="contamination_candidate.jsonl")
    ap.add_argument("--ambiguous", required=True, help="ambiguous.jsonl")
    ap.add_argument("--output-dir", default="processed/source_recovery")
    args = ap.parse_args()

    raw_path = Path(args.raw)
    input_paths = {
        "likely_valid": Path(args.likely),
        "contamination_candidate": Path(args.contamination),
        "ambiguous": Path(args.ambiguous),
    }
    for p in [raw_path, *input_paths.values()]:
        if not p.is_file():
            ap.error(f"File not found: {p}")

    # Preserve exact raw bytes for hash verification; decode strictly.
    raw_bytes = raw_path.read_bytes()
    raw_text = raw_bytes.decode("utf-8")
    raw_lines = raw_text.splitlines()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    counts = Counter()
    results = []
    seen_source_lines = {}
    duplicate_source_line_refs = []
    input_hashes = {}

    for bucket, path in input_paths.items():
        input_hashes[bucket] = digest(path)
        for jsonl_line, item in read_jsonl(path):
            counts["input_records"] += 1
            original = item.get("original_record", {})
            source_line = original.get("line")
            preview = original.get("text")
            truncated = original.get("truncated")
            status = "UNRESOLVED"
            full_text = None
            reason = ""

            if not isinstance(source_line, int) or isinstance(source_line, bool) or source_line < 1:
                reason = "missing_or_invalid_1_based_source_line"
            elif not isinstance(preview, str):
                reason = "missing_text_preview"
            elif source_line > len(raw_lines):
                reason = "source_line_out_of_range"
            else:
                full_text = raw_lines[source_line - 1]
                if truncated is True:
                    if full_text.startswith(preview):
                        status = "RECOVERED_PREFIX_MATCH"
                        reason = "raw_source_line_starts_with_saved_preview"
                        counts["recovered_truncated"] += 1
                    elif preview in full_text:
                        status = "RECOVERED_CONTAINS_PREVIEW"
                        reason = "preview_occurs_within_raw_source_line_but_not_at_start"
                        counts["recovered_nonprefix"] += 1
                    else:
                        status = "MISMATCH"
                        reason = "raw_source_line_does_not_match_saved_preview"
                        full_text = None
                        counts["mismatch"] += 1
                elif truncated is False:
                    if full_text == preview:
                        status = "SOURCE_MATCH_CONFIRMED"
                        reason = "nontruncated_preview_equals_raw_source_line"
                        counts["source_match_confirmed"] += 1
                    elif full_text.startswith(preview):
                        status = "SOURCE_HAS_MORE_TEXT"
                        reason = "preview_marked_nontruncated_but_raw_line_is_longer"
                        counts["source_has_more_text"] += 1
                    else:
                        status = "MISMATCH"
                        reason = "nontruncated_preview_does_not_match_raw_source_line"
                        full_text = None
                        counts["mismatch"] += 1
                else:
                    if full_text.startswith(preview):
                        status = "RECOVERED_PREFIX_MATCH_UNFLAGGED"
                        reason = "raw_source_starts_with_preview_but_truncated_flag_missing"
                        counts["unflagged_prefix_match"] += 1
                    elif full_text == preview:
                        status = "SOURCE_MATCH_CONFIRMED_FLAG_MISSING"
                        reason = "raw_source_equals_preview"
                        counts["source_match_confirmed"] += 1
                    else:
                        status = "MISMATCH"
                        reason = "no_truncation_flag_and_preview_mismatch"
                        full_text = None
                        counts["mismatch"] += 1

            if isinstance(source_line, int):
                if source_line in seen_source_lines:
                    duplicate_source_line_refs.append({
                        "source_line": source_line,
                        "first_bucket": seen_source_lines[source_line],
                        "duplicate_bucket": bucket,
                    })
                else:
                    seen_source_lines[source_line] = bucket

            counts[f"bucket_{bucket}"] += 1
            counts[f"status_{status}"] += 1
            results.append({
                "input_bucket": bucket,
                "input_jsonl_line": jsonl_line,
                "source_line_1_based": source_line,
                "truncated_flag": truncated,
                "recovery_status": status,
                "recovery_reason": reason,
                "original_classification_record": item,
                "recovered_full_text": full_text,
            })

    # Output every audit record; full text is populated only after source checks.
    audit_path = out / "source_recovery_audit.jsonl"
    with audit_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in results:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    recovered_path = out / "recovered_records.jsonl"
    with recovered_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in results:
            if row["recovery_status"].startswith("RECOVERED") or row["recovery_status"].startswith("SOURCE_MATCH"):
                f.write(json.dumps({
                    "input_bucket": row["input_bucket"],
                    "source_line_1_based": row["source_line_1_based"],
                    "recovery_status": row["recovery_status"],
                    "text": row["recovered_full_text"],
                }, ensure_ascii=False) + "\n")

    unresolved_path = out / "unresolved_records.jsonl"
    with unresolved_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in results:
            if row["recovery_status"] in ("UNRESOLVED", "MISMATCH", "SOURCE_HAS_MORE_TEXT"):
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    report = {
        "status": "PASS_WITH_REVIEW",
        "raw_source": str(raw_path.resolve()),
        "raw_source_bytes": len(raw_bytes),
        "raw_source_sha256": digest(raw_path),
        "raw_source_line_count": len(raw_lines),
        "input_files": {
            bucket: {"path": str(path.resolve()), "sha256": input_hashes[bucket]}
            for bucket, path in input_paths.items()
        },
        "counts": dict(sorted(counts.items())),
        "duplicate_source_line_references": duplicate_source_line_refs,
        "policy": [
            "Raw source and classification inputs are read-only.",
            "Source line references are interpreted as 1-based line numbers.",
            "Preview matching is checked before recovered text is accepted.",
            "No record is silently dropped or rewritten.",
            "A successful source recovery does not establish content quality or licensing.",
            "All recovered records still require content and provenance review.",
        ],
        "outputs": {
            "source_recovery_audit": str(audit_path.resolve()),
            "recovered_records": str(recovered_path.resolve()),
            "unresolved_records": str(unresolved_path.resolve()),
        },
    }
    report_path = out / "source_recovery_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nReport saved: {report_path.resolve()}")

if __name__ == "__main__":
    main()
