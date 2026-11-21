#!/usr/bin/env python3
"""Build a read-only human review register for IGRIS Tamil flagged records."""
from __future__ import annotations
import argparse, csv, hashlib, json, sys
from pathlib import Path

DECISIONS = {
    749: ("KEEP_WITH_CLEANUP_REVIEW", "Useful Tamil informational content; government URL embedded.", "Review URL formatting; retain useful Tamil prose."),
    1215: ("KEEP_WITH_CLEANUP_REVIEW", "Meaningful Tamil descriptive content with trailing HTML break.", "Review/remove trailing <br> only after human approval."),
    1602: ("KEEP_WITH_CLEANUP_REVIEW", "Tamil report text with an external URL.", "Review URL and surrounding punctuation; assess prose independently."),
    3480: ("KEEP_WITH_CLEANUP_REVIEW", "Tamil radio-history content with trailing HTML break.", "Review trailing <br>; retain content if source context is valid."),
    3514: ("KEEP_WITH_CLEANUP_REVIEW", "Meaningful but fragmentary Tamil biographical sentence; leading <br> and NBSP-like spacing.", "Review sentence completeness, leading markup and spacing."),
    4128: ("QUARANTINE_REVIEW", "Article text mixed with Previous Post/Next Post navigation and unrelated content.", "Separate coherent source passages only with provenance; otherwise retain in review quarantine."),
    4166: ("KEEP_WITH_CLEANUP_REVIEW", "Substantial Tamil literary interview; contains a website reference.", "Review URL separately; retain interview text."),
    4308: ("KEEP_WITH_CLEANUP_REVIEW", "Tamil informational content with a government website URL.", "Review URL separately; retain useful prose."),
    4578: ("QUARANTINE_REVIEW", "Literary announcement mixed with promotional/contact information.", "Human review whether promotional segment should be separated."),
    4789: ("QUARANTINE_REVIEW", "Temple news, cricket report and unrelated diet advertisement concatenated.", "Do not train on as one record; source-level segmentation/provenance review needed."),
    5073: ("KEEP_WITH_CLEANUP_REVIEW", "Tamil scientific/biographical content; markup flag appears to be a heuristic false positive in preview.", "Inspect NBSP and full source; do not remove content solely due to flag."),
    5781: ("KEEP_WITH_CLEANUP_REVIEW", "Tamil encyclopedic content with Wikipedia retrieval URL metadata.", "Review/remove retrieval metadata only after approval."),
    6055: ("QUARANTINE_REVIEW", "Biography mixed with Wikipedia retrieval metadata and unrelated religious-event content.", "Separate unrelated passages only with verified provenance; otherwise quarantine."),
    6132: ("KEEP_WITH_CLEANUP_REVIEW", "Tamil genomics explanation mixed with Wikipedia retrieval metadata.", "Review retrieval metadata; preserve technical English terms where appropriate."),
    6314: ("QUARANTINE_REVIEW", "Bus-accident report, related tags, unrelated Panchayat article and university news concatenated.", "Source segmentation/provenance review required."),
    6404: ("QUARANTINE_REVIEW", "Wikipedia metadata, unrelated car-search text and tourism content mixed together.", "Quarantine pending source-level separation and provenance."),
    6976: ("QUARANTINE_REVIEW", "Record consists of Wikipedia user-contribution retrieval metadata rather than meaningful prose.", "Do not include as a training text record unless source content is recovered and verified."),
    7377: ("QUARANTINE_REVIEW", "Record consists of a Wikipedia page URL/retrieval metadata.", "Do not include as a training text record unless source content is recovered and verified."),
    7421: ("QUARANTINE_REVIEW", "Dictionary/search keyword list mixed with unrelated political/news content.", "Quarantine pending source-level separation and provenance."),
    7754: ("QUARANTINE_REVIEW", "Wikipedia metadata mixed with multiple unrelated news passages.", "Quarantine pending source-level separation and provenance."),
    8103: ("KEEP_WITH_CLEANUP_REVIEW", "Substantial Tamil explanation about clocks with Wikipedia metadata and a possibly corrupted phrase.", "Review suspicious phrase and retrieval metadata; preserve valid explanation."),
    8697: ("QUARANTINE_REVIEW", "Short social-media headline with shortened URL.", "Review source rights/context; do not treat as general prose by default."),
    9145: ("QUARANTINE_REVIEW", "Tourism-map text, Wikipedia metadata and unrelated job advertisement concatenated.", "Quarantine pending source-level separation and provenance."),
    9675: ("KEEP_WITH_CLEANUP_REVIEW", "Meaningful Tamil sentence with leading <br> markup.", "Review/remove leading <br> only after human approval."),
}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clean", required=True, help="NFC deduplicated Tamil corpus TXT")
    ap.add_argument("--flagged", required=True, help="Stage 1 clean_flagged_records_review.jsonl")
    ap.add_argument("--out", required=True, help="Output directory")
    args = ap.parse_args()
    clean, flagged, out = Path(args.clean), Path(args.flagged), Path(args.out)
    if not clean.is_file() or not flagged.is_file():
        ap.error("Both --clean and --flagged must point to existing files.")
    out.mkdir(parents=True, exist_ok=True)

    # Read once; line numbers are 1-based source line references.
    lines = clean.read_text(encoding="utf-8").splitlines()
    flagged_rows = []
    with flagged.open("r", encoding="utf-8") as f:
        for n, raw in enumerate(f, 1):
            if raw.strip():
                obj = json.loads(raw)
                flagged_rows.append(obj)

    records, errors = [], []
    seen = set()
    for item in flagged_rows:
        line_no = item.get("source_line")
        if not isinstance(line_no, int) or line_no < 1 or line_no > len(lines):
            errors.append(f"Invalid/out-of-range source_line: {line_no!r}")
            continue
        if line_no in seen:
            errors.append(f"Duplicate flagged source_line: {line_no}")
            continue
        seen.add(line_no)
        if line_no not in DECISIONS:
            errors.append(f"No reviewed decision registered for source_line {line_no}")
            continue
        category, reason, notes = DECISIONS[line_no]
        full_text = lines[line_no - 1]
        preview = item.get("text_preview", "")
        # A mismatch is a warning only: preview may be shortened or transformed.
        preview_match = bool(preview) and (preview in full_text or full_text.startswith(preview))
        records.append({
            "source_line": line_no,
            "classification": category,
            "reason": reason,
            "proposed_cleanup_notes": notes,
            "flags": ";".join(item.get("flags", [])),
            "char_count_from_profile": item.get("char_count", ""),
            "tamil_char_count_from_profile": item.get("tamil_char_count", ""),
            "latin_char_count_from_profile": item.get("latin_char_count", ""),
            "preview_matches_source": preview_match,
            "human_approval_status": "PENDING",
            "full_original_text": full_text,
        })

    missing = sorted(set(DECISIONS) - seen)
    unexpected = sorted(seen - set(DECISIONS))
    counts = {"KEEP_WITH_CLEANUP_REVIEW": 0, "QUARANTINE_REVIEW": 0}
    for r in records:
        counts[r["classification"]] = counts.get(r["classification"], 0) + 1

    fields = list(records[0].keys()) if records else [
        "source_line","classification","reason","proposed_cleanup_notes","flags",
        "char_count_from_profile","tamil_char_count_from_profile","latin_char_count_from_profile",
        "preview_matches_source","human_approval_status","full_original_text"
    ]
    csv_path = out / "tamil_human_review_register.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(records)

    jsonl_path = out / "tamil_human_review_register.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    complete = not errors and not missing and not unexpected and len(records) == 24
    summary = {
        "status": "REGISTER_BUILT_REVIEW_REQUIRED" if complete else "REGISTER_BUILT_WITH_INPUT_GAPS",
        "records_in_flagged_input": len(flagged_rows),
        "records_registered": len(records),
        "classification_counts": counts,
        "missing_expected_source_lines": missing,
        "unexpected_source_lines": unexpected,
        "reference_errors": errors,
        "clean_source_sha256": sha256(clean),
        "flagged_input_sha256": sha256(flagged),
        "outputs": [csv_path.name, jsonl_path.name],
        "decision": "READ_ONLY_REGISTER_ONLY_NO_SOURCE_MODIFICATION_NO_DATASET_APPROVAL_NO_TRAINING",
        "human_approval_status": "PENDING_FOR_ALL_RECORDS",
    }
    (out / "tamil_review_register_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if complete else 2

if __name__ == "__main__":
    sys.exit(main())
