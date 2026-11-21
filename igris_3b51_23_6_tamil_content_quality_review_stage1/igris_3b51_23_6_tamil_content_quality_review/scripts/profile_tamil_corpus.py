#!/usr/bin/env python3
"""Read-only Tamil pilot corpus profiling; no approval or training."""
from __future__ import annotations
import argparse, collections, hashlib, json, re
from pathlib import Path

try:
    import unicodedata2 as ud
except ImportError:
    import unicodedata as ud

TAMIL = re.compile(r"[\u0B80-\u0BFF]")
LATIN = re.compile(r"[A-Za-z]")
URL = re.compile(r"(?:https?://|www\.)", re.I)
HTML = re.compile(r"<\s*(?:html|script|style|div|p|a|br|body|head)\b", re.I)
TOKENISH = re.compile(r"<\|[^|]{1,80}\|>")
REPLACEMENT = "\uFFFD"

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clean", required=True)
    ap.add_argument("--mixed", required=True)
    ap.add_argument("--quarantine", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sample-size", type=int, default=100)
    args = ap.parse_args()

    paths = {
        "clean": Path(args.clean),
        "mixed": Path(args.mixed),
        "quarantine": Path(args.quarantine),
    }
    missing = [f"{k}: {v}" for k, v in paths.items() if not v.is_file()]
    if missing:
        raise SystemExit("BLOCKED: missing input files:\n" + "\n".join(missing))
    if args.sample_size < 1 or args.sample_size > 1000:
        raise SystemExit("sample-size must be between 1 and 1000")

    raw = paths["clean"].read_bytes()
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as e:
        raise SystemExit(f"BLOCKED: clean file is not valid UTF-8: {e}")
    lines = text.splitlines()
    records = [(i, s) for i, s in enumerate(lines, 1) if s.strip()]
    if not records:
        raise SystemExit("BLOCKED: no non-empty clean records found")

    lengths = [len(s) for _, s in records]
    sorted_lengths = sorted(lengths)
    def percentile(p):
        idx = min(len(sorted_lengths)-1, int((p/100) * (len(sorted_lengths)-1)))
        return sorted_lengths[idx]

    duplicate_map = collections.defaultdict(list)
    flags = collections.Counter()
    script_counts = collections.Counter()
    char_counts = collections.Counter()
    review_rows = []
    for line_no, s in records:
        normalized = ud.normalize("NFC", s)
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        duplicate_map[digest].append(line_no)
        tamil_n = len(TAMIL.findall(s))
        latin_n = len(LATIN.findall(s))
        has_tamil, has_latin = tamil_n > 0, latin_n > 0
        script_counts["tamil_present" if has_tamil else "no_tamil"] += 1
        if has_latin:
            script_counts["latin_present"] += 1
        if has_tamil and has_latin:
            script_counts["tamil_and_latin"] += 1
        if not has_tamil:
            flags["no_tamil_script"] += 1
        if "\uFFFD" in s:
            flags["replacement_character"] += 1
        if "\x00" in s:
            flags["nul"] += 1
        if any(ord(c) < 32 and c not in "\t" for c in s):
            flags["control_character"] += 1
        if URL.search(s):
            flags["url_marker"] += 1
        if HTML.search(s):
            flags["html_or_markup_marker"] += 1
        if TOKENISH.search(s):
            flags["structural_token_spelling"] += 1
        if s != normalized:
            flags["not_nfc"] += 1
        if len(s) > 4000:
            flags["over_4000_chars"] += 1
        if len(s.strip()) < 5:
            flags["short_under_5_chars"] += 1
        for c in s:
            if TAMIL.fullmatch(c):
                char_counts[c] += 1
        reasons = []
        if not has_tamil: reasons.append("no_tamil_script")
        if "\uFFFD" in s: reasons.append("replacement_character")
        if "\x00" in s: reasons.append("nul")
        if any(ord(c) < 32 and c not in "\t" for c in s): reasons.append("control_character")
        if URL.search(s): reasons.append("url_marker")
        if HTML.search(s): reasons.append("html_or_markup_marker")
        if TOKENISH.search(s): reasons.append("structural_token_spelling")
        if s != normalized: reasons.append("not_nfc")
        if len(s) > 4000: reasons.append("over_4000_chars")
        if len(s.strip()) < 5: reasons.append("short_under_5_chars")
        if reasons:
            review_rows.append({
                "source_line": line_no,
                "char_count": len(s),
                "tamil_char_count": tamil_n,
                "latin_char_count": latin_n,
                "flags": reasons,
                "text_preview": s[:500],
            })

    duplicate_groups = [v for v in duplicate_map.values() if len(v) > 1]
    mixed_count = 0
    quarantine_count = 0
    with paths["mixed"].open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                mixed_count += 1
    with paths["quarantine"].open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                quarantine_count += 1

    # Deterministic, evenly spaced sample from clean records.
    n = min(args.sample_size, len(records))
    if n == 1:
        chosen = [records[len(records)//2]]
    else:
        indices = [round(i * (len(records)-1)/(n-1)) for i in range(n)]
        chosen = [records[i] for i in indices]
    sample = [{
        "source_line": line_no,
        "char_count": len(s),
        "text": s[:1200],
    } for line_no, s in chosen]

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "PROFILE_COMPLETE_REVIEW_REQUIRED",
        "decision": "READ_ONLY_PROFILING_ONLY_NO_CONTENT_APPROVAL_NO_LICENSE_APPROVAL_NO_TRAINING",
        "unicode_database_version": ud.unidata_version,
        "clean": {
            "path": str(paths["clean"]),
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "nonempty_records": len(records),
            "length_chars": {
                "min": min(lengths), "median": sorted_lengths[len(sorted_lengths)//2],
                "p95": percentile(95), "p99": percentile(99), "max": max(lengths),
            },
            "script_counts": dict(script_counts),
            "flagged_record_counts": dict(flags),
            "nfc_duplicate_groups": len(duplicate_groups),
            "records_in_nfc_duplicate_groups": sum(map(len, duplicate_groups)),
            "top_tamil_codepoints": [
                {"codepoint": f"U+{ord(c):04X}", "character": c, "count": count}
                for c, count in char_counts.most_common(40)
            ],
        },
        "review_groups": {
            "mixed_jsonl_records": mixed_count,
            "quarantine_jsonl_records": quarantine_count,
        },
        "sample_method": "deterministic evenly spaced records by source line; not random or statistically representative",
        "sample_size": len(sample),
        "limitations": [
            "Script-presence heuristics do not establish that a record is grammatically correct Tamil.",
            "Latin characters can be valid names, abbreviations, technical terms, or Tanglish; they are not automatically contamination.",
            "URL/markup markers are review flags, not automatic rejection criteria.",
            "NFC duplicate groups are exact normalized-text duplicates, not semantic duplicates.",
            "This profiler does not verify source provenance, copyright, license compatibility, or commercial-use rights.",
            "Review previews may contain sensitive or inappropriate source text; handle generated reports accordingly.",
        ],
        "input_hashes": {k: sha256(v) for k, v in paths.items()},
    }
    (out / "tamil_content_quality_profile.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out / "clean_flagged_records_review.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in review_rows),
        encoding="utf-8"
    )
    (out / "clean_stratified_sample_review.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in sample),
        encoding="utf-8"
    )
    print(json.dumps({
        "status": report["status"],
        "unicode_database_version": ud.unidata_version,
        "clean_nonempty_records": len(records),
        "mixed_jsonl_records": mixed_count,
        "quarantine_jsonl_records": quarantine_count,
        "flagged_record_counts": dict(flags),
        "nfc_duplicate_groups": len(duplicate_groups),
        "outputs": [
            str(out / "tamil_content_quality_profile.json"),
            str(out / "clean_flagged_records_review.jsonl"),
            str(out / "clean_stratified_sample_review.jsonl"),
        ],
        "decision": report["decision"],
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
