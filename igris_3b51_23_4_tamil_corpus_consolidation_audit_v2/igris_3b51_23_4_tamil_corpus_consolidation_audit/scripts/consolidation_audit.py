#!/usr/bin/env python3
"""Read-only inventory and cross-group duplicate audit for IGRIS Tamil pilot."""
from __future__ import annotations
import argparse, csv, hashlib, json, unicodedata
from pathlib import Path

TEXT_KEYS = ("text", "content", "original_text", "recovered_full_source_text")

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def load_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if line.strip():
                rows.append((line_no, json.loads(line)))
    return rows

def extract_text(obj):
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        for key in TEXT_KEYS:
            value = obj.get(key)
            if isinstance(value, str):
                return value
        # Known nested structures in the project's review records.
        for key in ("original_record", "original_classification_record", "original_record_text"):
            if key in obj:
                value = extract_text(obj[key])
                if value is not None:
                    return value
    return None

def summarize_text_group(name, records):
    found, unresolved = [], []
    for row_no, obj in records:
        text = extract_text(obj)
        if isinstance(text, str):
            found.append((row_no, text))
        else:
            unresolved.append(row_no)
    return found, unresolved

def norm_key(s):
    return unicodedata.normalize("NFC", s)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clean", required=True)
    ap.add_argument("--mixed", required=True)
    ap.add_argument("--quarantine", required=True)
    ap.add_argument("--recovered", required=True)
    ap.add_argument("--remediation-report", required=True)
    ap.add_argument("--closure-report", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    paths = {
        "clean": Path(a.clean), "mixed": Path(a.mixed),
        "quarantine": Path(a.quarantine), "recovered_review_only": Path(a.recovered),
        "remediation_report": Path(a.remediation_report),
        "closure_report": Path(a.closure_report),
    }
    missing = [f"{k}: {p}" for k,p in paths.items() if not p.is_file()]
    if missing:
        raise SystemExit("BLOCKED: missing input files:\n" + "\n".join(missing))

    clean_lines = paths["clean"].read_text(encoding="utf-8", errors="strict").splitlines()
    clean_records = [(i, s) for i,s in enumerate(clean_lines,1) if s != ""]
    mixed_jsonl = load_jsonl(paths["mixed"])
    quarantine_jsonl = load_jsonl(paths["quarantine"])
    recovered_jsonl = load_jsonl(paths["recovered_review_only"])
    remediation = load_json(paths["remediation_report"])
    closure = load_json(paths["closure_report"])

    groups = {"clean": clean_records}
    unresolved_text_fields = {}
    for name, records in (
        ("mixed", mixed_jsonl),
        ("quarantine", quarantine_jsonl),
        ("recovered_review_only", recovered_jsonl),
    ):
        found, unresolved = summarize_text_group(name, records)
        groups[name] = found
        unresolved_text_fields[name] = unresolved

    # Build NFC exact-text groups; preserve original group and row references.
    occurrences = {}
    for group_name, items in groups.items():
        for row_no, text in items:
            key = norm_key(text)
            if not key:
                continue
            occurrences.setdefault(key, []).append({
                "group": group_name, "row": row_no,
                "chars": len(text),
                "sha256_utf8": hashlib.sha256(text.encode("utf-8")).hexdigest()
            })

    duplicate_rows = []
    for key, refs in occurrences.items():
        distinct_groups = sorted({r["group"] for r in refs})
        if len(refs) > 1:
            duplicate_rows.append({
                "nfc_text_sha256": hashlib.sha256(key.encode("utf-8")).hexdigest(),
                "occurrence_count": len(refs),
                "groups": ";".join(distinct_groups),
                "references_json": json.dumps(refs, ensure_ascii=False),
                "duplicate_scope": "CROSS_GROUP" if len(distinct_groups) > 1 else "WITHIN_GROUP",
            })

    counts = {
        "clean_nonempty_lines": len(clean_records),
        "mixed_jsonl_records": len(mixed_jsonl),
        "mixed_text_extracted": len(groups["mixed"]),
        "mixed_text_unresolved": len(unresolved_text_fields["mixed"]),
        "quarantine_jsonl_records": len(quarantine_jsonl),
        "quarantine_text_extracted": len(groups["quarantine"]),
        "quarantine_text_unresolved": len(unresolved_text_fields["quarantine"]),
        "recovered_review_jsonl_records": len(recovered_jsonl),
        "recovered_text_extracted": len(groups["recovered_review_only"]),
        "recovered_text_unresolved": len(unresolved_text_fields["recovered_review_only"]),
        "duplicate_text_keys": len(duplicate_rows),
        "cross_group_duplicate_keys": sum(1 for r in duplicate_rows if r["duplicate_scope"] == "CROSS_GROUP"),
    }

    # Compare counts that the known reports actually declare.
    checks = {
        "clean_count_matches_remediation_report": counts["clean_nonempty_lines"] == remediation.get("accepted_unique_records"),
        "mixed_count_matches_remediation_report": counts["mixed_jsonl_records"] == remediation.get("mixed_script_review_records"),
        "quarantine_count_matches_remediation_report": counts["quarantine_jsonl_records"] == remediation.get("quarantined_records"),
        "recovered_count_matches_closure_report": counts["recovered_review_jsonl_records"] == closure.get("review_only_candidate_records_written"),
        "closure_status_is_pass_with_review": closure.get("status") == "PASS_WITH_REVIEW",
    }
    # Avoid claiming PASS if any input structure or declared count is inconsistent.
    unresolved_total = sum(len(v) for v in unresolved_text_fields.values())
    status = "PASS_WITH_REVIEW" if all(checks.values()) and unresolved_total == 0 else "REVIEW_REQUIRED"

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "status": status,
        "decision": "INVENTORY_AND_DUPLICATE_AUDIT_ONLY_NO_MERGE_NO_APPROVAL",
        "counts": counts,
        "report_consistency_checks": checks,
        "unresolved_text_extraction_rows": unresolved_text_fields,
        "input_files": {
            k: {"path": str(p), "bytes": p.stat().st_size, "sha256": sha256_file(p)}
            for k,p in paths.items()
        },
        "duplicate_review_policy": "Candidates are reported only; no records are deleted or merged.",
        "dataset_decisions": {
            "clean": "existing cleaned output; still subject to content and licensing review",
            "mixed": "review-only; not approved",
            "quarantine": "remain quarantined",
            "recovered_review_only": "review-only; do not merge into clean corpus",
        },
        "limitations": [
            "Exact NFC duplicate detection is not semantic duplicate detection.",
            "JSONL text extraction relies on known common text fields; unresolved rows are reported.",
            "This audit does not establish source provenance, attribution compliance, licensing, or commercial rights.",
            "No input files were modified."
        ]
    }
    (out / "tamil_consolidation_audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    csv_path = out / "cross_group_duplicate_candidates.csv"
    fields = ["nfc_text_sha256", "occurrence_count", "groups", "duplicate_scope", "references_json"]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(duplicate_rows)

    print(json.dumps({
        "status": status, "counts": counts,
        "report_consistency_checks": checks,
        "unresolved_text_extraction_total": unresolved_total,
        "outputs": [str(out / "tamil_consolidation_audit.json"), str(csv_path)],
        "decision": report["decision"]
    }, ensure_ascii=False, indent=2))
    if status != "PASS_WITH_REVIEW":
        raise SystemExit(2)

if __name__ == "__main__":
    main()
