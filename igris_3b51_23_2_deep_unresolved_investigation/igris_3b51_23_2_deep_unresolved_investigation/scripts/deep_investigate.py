#!/usr/bin/env python3
"""Read-only deep diagnostics for unresolved source-recovery records."""
from __future__ import annotations
import argparse, csv, hashlib, json, unicodedata
from pathlib import Path

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def get_nested(d, keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def first_diff(a: str, b: str):
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            return i
    return n if len(a) != len(b) else None

def cp_window(s: str, pos, radius=5):
    if pos is None:
        return ""
    lo, hi = max(0, pos-radius), min(len(s), pos+radius+1)
    return " ".join(f"{i}:{s[i]!r}=U+{ord(s[i]):04X}" for i in range(lo, hi))

def safe_decode_candidates(s: str):
    out = []
    for enc in ("latin-1", "cp1252"):
        try:
            b = s.encode(enc, errors="strict")
            repaired = b.decode("utf-8", errors="strict")
            out.append((enc, repaired))
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return out

def byte_common_prefix(a: str, b: str):
    aa, bb = a.encode("utf-8"), b.encode("utf-8")
    n = min(len(aa), len(bb))
    i = 0
    while i < n and aa[i] == bb[i]:
        i += 1
    return i, len(aa), len(bb)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--unresolved", required=True)
    ap.add_argument("--recovery-report", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rawp, unp, rep = Path(args.raw), Path(args.unresolved), Path(args.recovery_report)
    outp = Path(args.out)
    outp.mkdir(parents=True, exist_ok=True)

    recovery = json.loads(rep.read_text(encoding="utf-8"))
    raw_hash = sha256_file(rawp)
    expected = recovery.get("raw_source_sha256") or recovery.get("raw_source", {}).get("sha256")
    if not expected:
        raise SystemExit("BLOCKED: recovery report does not expose expected raw source SHA-256.")
    if raw_hash.lower() != str(expected).lower():
        raise SystemExit(f"BLOCKED: raw source SHA-256 mismatch. actual={raw_hash} expected={expected}")

    # Keep line endings out of comparisons, but do not trim spaces or normalize.
    raw_lines = rawp.read_text(encoding="utf-8", errors="strict").splitlines()
    records = []
    with unp.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if line.strip():
                records.append((lineno, json.loads(line)))

    details, csv_rows = [], []
    for idx, (jsonl_line, rec) in enumerate(records, 1):
        src_line_no = rec.get("source_line_1_based")
        preview = get_nested(rec, ("original_classification_record", "original_record", "text"))
        truncated = bool(rec.get("truncated_flag"))
        item = {
            "case": idx, "unresolved_jsonl_line": jsonl_line,
            "source_line_1_based": src_line_no, "truncated_flag": truncated,
            "original_recovery_status": rec.get("recovery_status"),
            "preview_present": isinstance(preview, str),
        }
        if not isinstance(src_line_no, int) or not (1 <= src_line_no <= len(raw_lines)):
            item.update({"comparison": "INVALID_SOURCE_LINE", "error": "source line reference out of range"})
            details.append(item); continue
        if not isinstance(preview, str):
            item.update({"comparison": "MISSING_PREVIEW", "error": "preview text missing"})
            details.append(item); continue

        source = raw_lines[src_line_no - 1]
        npreview, nsource = unicodedata.normalize("NFC", preview), unicodedata.normalize("NFC", source)
        if preview == source:
            comparison = "EXACT_MATCH"
        elif npreview == nsource:
            comparison = "NFC_MATCH"
        elif truncated and source.startswith(preview):
            comparison = "TRUNCATED_PREFIX_MATCH"
        elif truncated and nsource.startswith(npreview):
            comparison = "TRUNCATED_NFC_PREFIX_MATCH"
        else:
            comparison = "NO_MATCH"

        diff = first_diff(preview, source)
        bcp, pbytes, sbytes = byte_common_prefix(preview, source)
        repairs = []
        for enc, candidate in safe_decode_candidates(preview):
            c_nfc = unicodedata.normalize("NFC", candidate)
            if candidate == source:
                relation = "EXACT_MATCH"
            elif c_nfc == nsource:
                relation = "NFC_MATCH"
            elif truncated and source.startswith(candidate):
                relation = "TRUNCATED_PREFIX_MATCH"
            elif truncated and nsource.startswith(c_nfc):
                relation = "TRUNCATED_NFC_PREFIX_MATCH"
            else:
                relation = "NO_MATCH"
            repairs.append({
                "method": f"encode_{enc}_then_decode_utf8",
                "relation_to_source": relation,
                "candidate_chars": len(candidate),
                "candidate_equals_source": candidate == source,
            })

        item.update({
            "comparison": comparison,
            "preview_chars": len(preview), "source_chars": len(source),
            "preview_utf8_bytes": len(preview.encode("utf-8")),
            "source_utf8_bytes": len(source.encode("utf-8")),
            "first_differing_character_index_zero_based": diff,
            "preview_codepoints_near_first_difference": cp_window(preview, diff),
            "source_codepoints_near_first_difference": cp_window(source, diff),
            "utf8_common_prefix_bytes": bcp,
            "preview_utf8_bytes_total": pbytes,
            "source_utf8_bytes_total": sbytes,
            "preview_is_source_prefix": source.startswith(preview),
            "source_is_preview_prefix": preview.startswith(source),
            "nfc_preview_is_nfc_source_prefix": nsource.startswith(npreview),
            "diagnostic_encoding_candidates": repairs,
            "source_line_sha256_utf8": hashlib.sha256(source.encode("utf-8")).hexdigest(),
            "preview_sha256_utf8": hashlib.sha256(preview.encode("utf-8")).hexdigest(),
        })
        details.append(item)
        csv_rows.append({
            "case": idx, "source_line_1_based": src_line_no,
            "truncated_flag": truncated, "comparison": comparison,
            "preview_chars": len(preview), "source_chars": len(source),
            "first_diff_index": "" if diff is None else diff,
            "utf8_common_prefix_bytes": bcp,
            "preview_is_source_prefix": source.startswith(preview),
            "nfc_preview_is_nfc_source_prefix": nsource.startswith(npreview),
            "diagnostic_encoding_candidates": json.dumps(repairs, ensure_ascii=False),
        })

    counts = {}
    for x in details:
        k = x.get("comparison", "UNKNOWN")
        counts[k] = counts.get(k, 0) + 1
    report = {
        "status": "PASS_WITH_REVIEW",
        "raw_source_sha256": raw_hash,
        "raw_source_hash_matches_recovery_report": True,
        "raw_source_line_count": len(raw_lines),
        "unresolved_records_checked": len(records),
        "comparison_counts": counts,
        "cases": details,
        "decision": "DIAGNOSTIC_ONLY_NO_RECORDS_APPROVED",
        "notes": [
            "Read-only: source and unresolved inputs were not modified.",
            "Prefix matching is allowed only when truncated_flag is true.",
            "Encoding repairs are diagnostic candidates only and never rewrite records.",
            "NO_MATCH records remain unresolved; manual review is required.",
            "This report does not establish dataset quality, licensing, provenance, or commercial rights."
        ]
    }
    (outp / "deep_unresolved_investigation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with (outp / "deep_unresolved_character_diff.csv").open("w", newline="", encoding="utf-8-sig") as f:
        fields = list(csv_rows[0].keys()) if csv_rows else ["case", "source_line_1_based", "comparison"]
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(csv_rows)
    print(json.dumps({
        "status": report["status"],
        "raw_source_hash_matches_recovery_report": True,
        "unresolved_records_checked": len(records),
        "comparison_counts": counts,
        "outputs": [
            str(outp / "deep_unresolved_investigation.json"),
            str(outp / "deep_unresolved_character_diff.csv")
        ],
        "decision": report["decision"]
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
