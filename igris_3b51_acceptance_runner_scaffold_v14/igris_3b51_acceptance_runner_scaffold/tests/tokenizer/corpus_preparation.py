"""Local-only, auditable UTF-8 corpus preparation for IGRIS tokenizer training.

Reads only explicitly supplied files. Never downloads data, installs packages,
modifies source files, or trains a tokenizer. Writes a new prepared corpus and
JSON report into a caller-selected output directory that must not already exist.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable

from .acceptance_config import UNICODE_VERSION
from .unicode_security import escape_text, normalize_nfc
from .validation import require_text


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _resolve_inputs(paths: Iterable[str | Path]) -> list[Path]:
    resolved = [Path(p).expanduser().resolve() for p in paths]
    if not resolved:
        raise ValueError("supply at least one explicit UTF-8 corpus file")
    if len(set(resolved)) != len(resolved):
        raise ValueError("duplicate input file paths are not allowed")
    for path in resolved:
        if not path.is_file():
            raise FileNotFoundError(f"corpus input is not a file: {path}")
        if path.stat().st_size == 0:
            raise ValueError(f"corpus input is empty: {path}")
    return resolved


def prepare_corpus(
    input_files: Iterable[str | Path],
    output_dir: str | Path,
    *,
    mode: str = "text_mode",
    deduplicate: bool = False,
) -> tuple[Path, Path, dict]:
    """Prepare explicitly supplied UTF-8 text files, preserving record order.

    Each input line becomes one output line. In text_mode, NFC is applied before
    structural-spelling escaping. exact_unicode_mode preserves code points before
    escaping. Duplicate records are counted; removal occurs only when explicitly
    requested. Blank records and surrounding whitespace are preserved.
    """
    if mode not in ("text_mode", "exact_unicode_mode"):
        raise ValueError("mode must be text_mode or exact_unicode_mode")
    if type(deduplicate) is not bool:
        raise TypeError("deduplicate must be bool")
    sources = _resolve_inputs(input_files)
    output = Path(output_dir).expanduser().resolve()
    if output.exists():
        raise FileExistsError(f"output directory already exists; choose a new path: {output}")

    prepared_records: list[str] = []
    seen: set[str] = set()
    duplicate_records = 0
    removed_duplicate_records = 0
    blank_records = 0
    input_records = 0
    source_info = []

    for source in sources:
        source_info.append({"path": str(source), "bytes": source.stat().st_size, "sha256": _sha256(source)})
        # newline=None translates CRLF/CR to LF as record separators; record content
        # is otherwise preserved, including leading/trailing spaces.
        with source.open("r", encoding="utf-8", errors="strict", newline=None) as stream:
            for raw_line in stream:
                record = raw_line[:-1] if raw_line.endswith("\n") else raw_line
                require_text(record)
                if "\x00" in record:
                    raise ValueError(f"NUL character is not permitted (file {source}, record {input_records + 1})")
                input_records += 1
                if record == "":
                    blank_records += 1
                if mode == "text_mode":
                    record = normalize_nfc(record)
                encoded = escape_text(record, mode="exact_unicode_mode")
                if encoded in seen:
                    duplicate_records += 1
                    if deduplicate:
                        removed_duplicate_records += 1
                        continue
                else:
                    seen.add(encoded)
                prepared_records.append(encoded)

    if input_records == 0:
        raise ValueError("corpus inputs contain no records")
    if not prepared_records or all(item == "" for item in prepared_records):
        raise ValueError("corpus contains no non-empty training records")

    output.mkdir(parents=True, exist_ok=False)
    corpus_path = output / "prepared_corpus.txt"
    report_path = output / "corpus_report.json"
    # UTF-8 output with LF record separators; no BOM.
    with corpus_path.open("w", encoding="utf-8", newline="\n") as stream:
        for record in prepared_records:
            stream.write(record)
            stream.write("\n")

    report = {
        "project": "IGRIS",
        "project_version": "2.2.28",
        "pipeline": "3B.51.12",
        "mode": mode,
        "unicode_version": UNICODE_VERSION,
        "normalization": "NFC before escaping" if mode == "text_mode" else "none; code points preserved",
        "escaping": "U+F0000 sentinel, U+2581 W; and fixed S00-S11 structural escapes",
        "input_files": source_info,
        "input_record_count": input_records,
        "output_record_count": len(prepared_records),
        "blank_record_count": blank_records,
        "duplicate_record_count": duplicate_records,
        "deduplication_enabled": deduplicate,
        "records_removed_as_duplicates": removed_duplicate_records,
        "output_bytes": corpus_path.stat().st_size,
        "output_sha256": _sha256(corpus_path),
        "quality_notes": [
            "Record order is preserved across the supplied files.",
            "Blank records and surrounding whitespace are preserved.",
            "Duplicates are reported; they are removed only when --deduplicate is supplied.",
            "This report does not establish language balance, licensing, consent, or corpus representativeness.",
            "No tokenizer training was performed.",
        ],
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return corpus_path, report_path, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare local IGRIS UTF-8 tokenizer corpus; no downloads or training.")
    parser.add_argument("--input", action="append", required=True, help="Input UTF-8 text file; repeat for multiple files")
    parser.add_argument("--output-dir", required=True, help="New output directory; must not already exist")
    parser.add_argument("--mode", choices=("text_mode", "exact_unicode_mode"), default="text_mode")
    parser.add_argument("--deduplicate", action="store_true", help="Explicitly remove duplicate prepared records")
    args = parser.parse_args(argv)
    corpus, report, data = prepare_corpus(args.input, args.output_dir, mode=args.mode, deduplicate=args.deduplicate)
    print(f"Prepared corpus: {corpus}")
    print(f"Report: {report}")
    print(f"Input records: {data['input_record_count']}; output records: {data['output_record_count']}; duplicates: {data['duplicate_record_count']}")
    print("Training performed: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
