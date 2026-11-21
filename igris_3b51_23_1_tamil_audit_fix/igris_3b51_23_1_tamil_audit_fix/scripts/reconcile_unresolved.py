#!/usr/bin/env python3
"""Read-only Tamil pilot source reconciliation; understands nested recovery JSONL."""
import argparse, csv, hashlib, json, unicodedata
from pathlib import Path

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except Exception as exc:
                    raise ValueError(f"Invalid JSONL at {path}:{n}: {exc}")
    return rows

def get_preview(item):
    # Actual schema in this milestone:
    # item.original_classification_record.original_record.text
    outer = item.get("original_classification_record") or {}
    original = outer.get("original_record") or {}
    if isinstance(original.get("text"), str):
        return original["text"]
    # Backward-compatible fallback paths, without assuming they exist.
    for candidate in (item.get("text"), item.get("preview"),
                      item.get("saved_preview"), item.get("original_text")):
        if isinstance(candidate, str):
            return candidate
    return None

def repair_mojibake_candidates(s):
    """Try reversible UTF-8-bytes-misread-as-Latin1/CP1252 repairs."""
    out = []
    for enc in ("latin-1", "cp1252"):
        try:
            fixed = s.encode(enc).decode("utf-8")
            if fixed != s and fixed not in out:
                out.append(fixed)
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return out

def compare(source, preview):
    if preview is None:
        return "NO_PREVIEW", None
    if source == preview:
        return "EXACT_MATCH", preview
    if unicodedata.normalize("NFC", source) == unicodedata.normalize("NFC", preview):
        return "NFC_MATCH", preview
    for fixed in repair_mojibake_candidates(preview):
        if source == fixed:
            return "MOJIBAKE_REPAIRED_EXACT", fixed
        if unicodedata.normalize("NFC", source) == unicodedata.normalize("NFC", fixed):
            return "MOJIBAKE_REPAIRED_NFC", fixed
        # Prefix check is appropriate only for records explicitly marked truncated.
    return "NO_MATCH", None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--unresolved", required=True)
    ap.add_argument("--recovery-report", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    raw_path = Path(args.raw)
    unresolved_path = Path(args.unresolved)
    report_path = Path(args.recovery_report)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    raw_bytes = raw_path.read_bytes()
    raw_sha = hashlib.sha256(raw_bytes).hexdigest()
    raw_text = raw_bytes.decode("utf-8", errors="strict")
    source_lines = raw_text.splitlines()
    unresolved = load_jsonl(unresolved_path)
    prior_report = load_json(report_path)

    expected_sha = prior_report.get("raw_source_sha256")
    source_hash_ok = (raw_sha == expected_sha)
    cases = []
    for idx, item in enumerate(unresolved, 1):
        line_no = item.get("source_line_1_based")
        preview = get_preview(item)
        truncated = bool(item.get("truncated_flag", item.get("truncated", False)))
        old_status, repaired = ("INVALID_LINE_REFERENCE", None)
        if isinstance(line_no, int) and 1 <= line_no <= len(source_lines):
            src = source_lines[line_no - 1]
            old_status, repaired = compare(src, preview)
            if old_status == "NO_MATCH" and truncated and preview is not None:
                for fixed in repair_mojibake_candidates(preview):
                    if src.startswith(fixed):
                        old_status, repaired = "MOJIBAKE_REPAIRED_PREFIX", fixed
                        break
                if old_status == "NO_MATCH" and src.startswith(preview):
                    old_status, repaired = "PREFIX_MATCH", preview
            elif old_status == "NO_MATCH" and preview is not None and src.startswith(preview):
                old_status, repaired = "PREFIX_MATCH", preview
        cases.append({
            "case": idx,
            "source_line_1_based": line_no,
            "recovery_status_original": item.get("recovery_status"),
            "truncated_flag": truncated,
            "comparison": old_status,
            "preview_present": preview is not None,
            "preview_chars": len(preview) if preview is not None else 0,
            "source_chars": len(src) if isinstance(line_no, int) and 1 <= line_no <= len(source_lines) else None,
            "preview_encoding_repaired": old_status.startswith("MOJIBAKE_REPAIRED"),
        })

    counts = {}
    for c in cases:
        counts[c["comparison"]] = counts.get(c["comparison"], 0) + 1

    blockers = []
    reviews = []
    if not source_hash_ok:
        blockers.append("raw_source_sha256_does_not_match_recovery_report")
    if any(c["comparison"] in ("NO_MATCH", "NO_PREVIEW", "INVALID_LINE_REFERENCE") for c in cases):
        reviews.append("one_or_more_unresolved_records_need_manual_review")
    if any(c["comparison"].startswith("MOJIBAKE_REPAIRED") for c in cases):
        reviews.append("mojibake_repair_was_used; inspect original classification encoding/provenance")
    status = "BLOCKED" if blockers else ("PASS_WITH_REVIEW" if reviews or True else "PASS")

    with open(out / "unresolved_case_comparison.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(cases[0].keys()) if cases else ["case"])
        w.writeheader()
        w.writerows(cases)

    result = {
        "status": status,
        "raw_source": str(raw_path),
        "raw_source_bytes": len(raw_bytes),
        "raw_source_sha256": raw_sha,
        "recovery_report_expected_sha256": expected_sha,
        "raw_source_hash_matches_recovery_report": source_hash_ok,
        "raw_source_line_count": len(source_lines),
        "unresolved_records_checked": len(unresolved),
        "comparison_counts": counts,
        "cases": cases,
        "blockers": blockers,
        "review_items": reviews,
        "notes": [
            "Read-only: no input files were modified.",
            "The script reads the preview from original_classification_record.original_record.text.",
            "Mojibake repair is attempted only as a diagnostic comparison; original records are not rewritten.",
            "A prefix match is not proof that a truncated record has been fully recovered.",
            "This comparison does not approve content quality, dataset inclusion, licensing, or commercial rights."
        ]
    }
    (out / "tamil_source_reconciliation_report.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if blockers else 0

if __name__ == "__main__":
    raise SystemExit(main())
