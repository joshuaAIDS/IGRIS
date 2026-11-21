#!/usr/bin/env python3
"""Conservative, review-oriented classifier for Tamil/Latin mixed-script JSONL.

No record is deleted. Every input record is copied to all_records_preserved.jsonl
and assigned to exactly one primary bucket: likely_valid, contamination_candidate,
or ambiguous. Heuristics are indicators, not proof of contamination.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

URL_RE = re.compile(r"(?:https?://|www\.)\S+", re.I)
HTML_RE = re.compile(r"</?[A-Za-z][^>]*>|<!DOCTYPE|&(?:nbsp|amp|lt|gt);", re.I)
SCRIPT_RE = re.compile(
    r"\b(?:function\s*\(|document\.|window\.|var\s+\w+\s*=|"
    r"const\s+\w+\s*=|let\s+\w+\s*=|<\/?script\b|javascript:)\b", re.I
)
SEO_RE = re.compile(
    r"\b(?:meta\s+description|search\s+engine|all\s+rights\s+reserved|"
    r"privacy\s+policy|cookie\s+policy|related\s+articles|read\s+more|"
    r"subscribe\s+now|navigation|skip\s+to\s+content)\b", re.I
)
NAV_RE = re.compile(r"\b(?:home\s*[|>]\s*|login|sign\s*up|menu|search\s+this\s+site)\b", re.I)
TAMIL_RE = re.compile(r"[\u0B80-\u0BFF]")
LATIN_RE = re.compile(r"[A-Za-z]")
TOKEN_RE = re.compile(r"<\|[^|]{1,80}\|>|<think>|</think>|<action>|</action>", re.I)

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def collect_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from collect_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from collect_strings(v)

def choose_text(obj):
    # Prefer common text-bearing keys, otherwise concatenate all string values.
    preferred = ("text", "content", "sentence", "record", "line", "body")
    if isinstance(obj, dict):
        for key in preferred:
            value = obj.get(key)
            if isinstance(value, str):
                return value
    return "\n".join(collect_strings(obj))

def classify(text: str):
    tamil = bool(TAMIL_RE.search(text))
    latin = bool(LATIN_RE.search(text))
    indicators = {
        "url": bool(URL_RE.search(text)),
        "html": bool(HTML_RE.search(text)),
        "script": bool(SCRIPT_RE.search(text)),
        "seo_or_navigation": bool(SEO_RE.search(text) or NAV_RE.search(text)),
        "structural_token_like": bool(TOKEN_RE.search(text)),
    }
    strong = any(indicators[k] for k in ("html", "script", "seo_or_navigation"))
    if strong:
        bucket = "contamination_candidate"
        reason = "web_markup_script_or_navigation_indicator"
    elif indicators["url"] or indicators["structural_token_like"]:
        bucket = "ambiguous"
        reason = "url_or_structural_token_requires_contextual_review"
    elif tamil and latin:
        bucket = "likely_valid"
        reason = "tamil_and_latin_without_strong_contamination_indicators"
    else:
        bucket = "ambiguous"
        reason = "mixed_script_or_record_context_not_established"
    return bucket, reason, indicators, tamil, latin

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to tamil_mixed_script_review.jsonl")
    ap.add_argument("--output-dir", default="processed/mixed_script_classification")
    args = ap.parse_args()
    src = Path(args.input)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    if not src.is_file():
        ap.error(f"Input file not found: {src}")
    raw = src.read_bytes()
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        print(json.dumps({"status":"FAIL","error":f"Invalid UTF-8: {e}"}), file=sys.stderr)
        return 2

    buckets = {
        "likely_valid": [],
        "contamination_candidate": [],
        "ambiguous": [],
    }
    reasons = Counter()
    indicator_counts = Counter()
    total = 0
    malformed = 0
    for line_no, line in enumerate(decoded.splitlines(), 1):
        if not line.strip():
            continue
        total += 1
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            record = {"_raw_line": line}
        text = choose_text(record)
        bucket, reason, indicators, has_tamil, has_latin = classify(text)
        enriched = {
            "source_line": line_no,
            "primary_classification": bucket,
            "classification_reason": reason,
            "has_tamil_script": has_tamil,
            "has_latin_letters": has_latin,
            "indicators": indicators,
            "original_record": record,
        }
        buckets[bucket].append(enriched)
        reasons[reason] += 1
        for name, found in indicators.items():
            if found:
                indicator_counts[name] += 1

    # Keep a complete, unchanged logical copy of each parsed input record.
    # The enriched buckets are additive review metadata, not destructive edits.
    for name, rows in buckets.items():
        with (out / f"{name}.jsonl").open("w", encoding="utf-8", newline="\n") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    with (out / "all_records_preserved.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for line in decoded.splitlines():
            if line.strip():
                f.write(line + "\n")

    report = {
        "status": "PASS_WITH_REVIEW" if total and malformed == 0 else "PASS_WITH_REVIEW",
        "input": str(src.resolve()),
        "input_bytes": len(raw),
        "input_sha256": sha256(src),
        "utf8_valid": True,
        "input_nonempty_records": total,
        "malformed_json_lines": malformed,
        "classification_counts": {k: len(v) for k, v in buckets.items()},
        "classification_reason_counts": dict(sorted(reasons.items())),
        "indicator_record_counts": dict(sorted(indicator_counts.items())),
        "policy": [
            "No source record is deleted.",
            "all_records_preserved.jsonl retains every non-empty input line.",
            "Classification is heuristic and is not proof of contamination.",
            "likely_valid records still require sampling and human review.",
            "URLs and structural-token-like text are ambiguous, not automatically discarded.",
            "Do not use these classifications as licensing or commercial-rights approval."
        ],
        "outputs": {
            "all_records_preserved": "all_records_preserved.jsonl",
            "likely_valid": "likely_valid.jsonl",
            "contamination_candidate": "contamination_candidate.jsonl",
            "ambiguous": "ambiguous.jsonl",
        }
    }
    report_path = out / "mixed_script_classification_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nReport saved: {report_path.resolve()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
