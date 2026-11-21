#!/usr/bin/env python3
"""Read-only quality audit for the IGRIS Tamil pilot corpus."""
from __future__ import annotations
import argparse, collections, hashlib, json, statistics, sys, unicodedata
from pathlib import Path

STRUCTURAL = [
    "<|pad|>", "<|begin_of_text|>", "<|end_of_text|>", "<think>",
    "</think>", "<action>", "</action>", "<action_result>",
    "</action_result>", "<|system|>", "<|user|>", "<|assistant|>",
]
TAMIL_START, TAMIL_END = 0x0B80, 0x0BFF

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def percentile(values, p):
    if not values:
        return None
    vals = sorted(values)
    idx = round((len(vals) - 1) * p)
    return vals[idx]

def audit(path: Path) -> dict:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    try:
        text = raw.decode("utf-8", errors="strict")
        utf8_valid = True
        utf8_error = None
    except UnicodeDecodeError as exc:
        return {
            "status": "FAIL",
            "input": str(path),
            "input_bytes": len(raw),
            "input_sha256": digest,
            "utf8_valid": False,
            "utf8_error": str(exc),
            "note": "No decoding with replacement was performed; audit stopped."
        }

    lines = text.splitlines()
    nonempty = [line for line in lines if line.strip()]
    lengths = [len(line) for line in nonempty]
    exact_counts = collections.Counter(nonempty)
    duplicates = sum(n - 1 for n in exact_counts.values() if n > 1)
    nfc_mismatch = sum(1 for line in nonempty if unicodedata.normalize("NFC", line) != line)
    tamil_chars = 0
    latin_chars = 0
    other_letters = 0
    replacement_chars = 0
    nul_chars = 0
    control_chars = 0
    structural_hits = collections.Counter()
    non_tamil_records = 0
    mixed_script_records = 0
    tamil_records = 0
    sample_non_tamil = []
    for line_no, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        has_tamil = False
        has_latin = False
        for ch in line:
            cp = ord(ch)
            cat = unicodedata.category(ch)
            if TAMIL_START <= cp <= TAMIL_END:
                tamil_chars += 1
                has_tamil = True
            elif ("LATIN" in unicodedata.name(ch, "")) and cat.startswith("L"):
                latin_chars += 1
                has_latin = True
            elif cat.startswith("L"):
                other_letters += 1
            if ch == "\ufffd":
                replacement_chars += 1
            if cp == 0:
                nul_chars += 1
            if cat == "Cc" and ch not in "\t":
                control_chars += 1
        if has_tamil:
            tamil_records += 1
        else:
            non_tamil_records += 1
            if len(sample_non_tamil) < 10:
                sample_non_tamil.append({"line": line_no, "preview": line[:160]})
        if has_tamil and has_latin:
            mixed_script_records += 1
        for token in STRUCTURAL:
            if token in line:
                structural_hits[token] += 1

    report = {
        "status": "PASS_WITH_REVIEW" if utf8_valid else "FAIL",
        "input": str(path),
        "input_bytes": len(raw),
        "input_sha256": digest,
        "utf8_valid": utf8_valid,
        "line_count_including_blank": len(lines),
        "nonempty_records": len(nonempty),
        "blank_records": len(lines) - len(nonempty),
        "exact_duplicate_records_beyond_first": duplicates,
        "unique_nonempty_records": len(exact_counts),
        "nfc_mismatch_records": nfc_mismatch,
        "unicode_database_version": unicodedata.unidata_version,
        "characters": {
            "tamil_block": tamil_chars,
            "latin_letters": latin_chars,
            "other_script_letters": other_letters,
            "replacement_characters_U+FFFD": replacement_chars,
            "NUL_characters": nul_chars,
            "control_characters_excluding_tab": control_chars
        },
        "record_script_profile": {
            "records_with_tamil": tamil_records,
            "records_without_tamil": non_tamil_records,
            "records_mixing_tamil_and_latin": mixed_script_records,
            "non_tamil_record_samples_for_manual_review": sample_non_tamil
        },
        "record_length_characters": {
            "min": min(lengths) if lengths else None,
            "median": statistics.median(lengths) if lengths else None,
            "p95": percentile(lengths, .95),
            "p99": percentile(lengths, .99),
            "max": max(lengths) if lengths else None
        },
        "structural_token_occurrences_by_record": dict(structural_hits),
        "review_flags": []
    }
    if nfc_mismatch:
        report["review_flags"].append("Some records are not NFC; do not silently normalize without preserving the approved preprocessing policy.")
    if duplicates:
        report["review_flags"].append("Exact duplicate records exist.")
    if non_tamil_records:
        report["review_flags"].append("Records without Tamil script need manual language/content review.")
    if mixed_script_records:
        report["review_flags"].append("Mixed Tamil-Latin records exist; inspect whether they are intended.")
    if replacement_chars or nul_chars or control_chars:
        report["review_flags"].append("Suspicious Unicode/control characters exist.")
    if structural_hits:
        report["review_flags"].append("Reserved structural-token spellings occur in source text; review/escape under the approved tokenizer contract.")
    if not nonempty:
        report["review_flags"].append("No non-empty records found.")
    return report

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to acquired Tamil TXT corpus")
    ap.add_argument("--output", default="tamil_quality_report.json")
    args = ap.parse_args()
    path = Path(args.input).expanduser().resolve()
    out = Path(args.output).expanduser().resolve()
    if not path.is_file():
        print(f"ERROR: input file not found: {path}", file=sys.stderr)
        sys.exit(2)
    result = audit(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\nReport saved: {out}")
    if result["status"] == "FAIL":
        sys.exit(1)

if __name__ == "__main__":
    main()
