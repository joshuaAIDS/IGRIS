#!/usr/bin/env python3
"""Prepare a conservative IGRIS tokenizer pilot from locally supplied TXT/JSONL/CSV files.
No network access, training, or source acquisition is performed by this script.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
TAMIL_RE = re.compile(r"[\u0B80-\u0BFF]")
LATIN_RE = re.compile(r"[A-Za-z]")
WS_RE = re.compile(r"\s+")
MAX_CHARS = 4000

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def records(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".txt":
        with path.open("r", encoding="utf-8-sig", errors="strict") as f:
            yield from f
    elif suffix == ".jsonl":
        with path.open("r", encoding="utf-8-sig", errors="strict") as f:
            for line in f:
                if not line.strip():
                    continue
                obj = json.loads(line)
                if isinstance(obj, str):
                    yield obj
                elif isinstance(obj, dict):
                    for key in ("text", "sentence", "comment", "content"):
                        if isinstance(obj.get(key), str):
                            yield obj[key]
                            break
    elif suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                for key in ("text", "sentence", "comment", "content"):
                    if row.get(key):
                        yield row[key]
                        break

def classify(text: str) -> str:
    has_tamil = bool(TAMIL_RE.search(text))
    has_latin = bool(LATIN_RE.search(text))
    if has_tamil and has_latin:
        return "mixed_script"
    if has_tamil:
        return "tamil"
    if has_latin:
        # This is only a script-level bucket. Human review is required to
        # distinguish English from romanized Tamil/Tanglish.
        return "latin_review"
    return "other"

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    seen = set()
    outputs = {k: [] for k in ("tamil", "latin_review", "mixed_script", "other")}
    report = {"files": [], "records_read": 0, "empty": 0, "too_long": 0,
              "duplicates": 0, "invalid_files": [], "buckets": {}}
    for path in sorted(RAW.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".txt", ".jsonl", ".csv"}:
            continue
        file_info = {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
        try:
            count = 0
            for raw in records(path):
                report["records_read"] += 1
                text = unicodedata.normalize("NFC", str(raw))
                text = WS_RE.sub(" ", text).strip()
                if not text:
                    report["empty"] += 1
                    continue
                if len(text) > MAX_CHARS:
                    report["too_long"] += 1
                    continue
                # Do not silently remove special-looking strings. Flag them for review.
                if any(tok in text for tok in ("<|", "|>", "[INST]", "</s>")):
                    continue
                key = text.casefold()
                if key in seen:
                    report["duplicates"] += 1
                    continue
                seen.add(key)
                bucket = classify(text)
                outputs[bucket].append(text)
                count += 1
            file_info["accepted_unique_records"] = count
            report["files"].append(file_info)
        except (UnicodeError, json.JSONDecodeError, csv.Error) as exc:
            report["invalid_files"].append({"path": str(path), "error": str(exc)})
    for bucket, rows in outputs.items():
        target = OUT / f"{bucket}.txt"
        target.write_text("".join(x + "\n" for x in rows), encoding="utf-8")
        report["buckets"][bucket] = {
            "records": len(rows),
            "sha256": sha256(target)
        }
    report["note"] = (
        "latin_review is NOT automatically split into English and Tanglish. "
        "Manually label a reviewed sample before balancing or training. "
        "This pilot script performs no training and downloads no data."
    )
    (REPORTS / "pilot_quality_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["invalid_files"]:
        sys.exit(2)

if __name__ == "__main__":
    main()
