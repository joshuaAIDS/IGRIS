#!/usr/bin/env python3
"""Stream the first N newline-delimited records from IndicCorpV2 data/ta.txt.

This avoids the unsupported Hugging Face dataset-viewer /rows API for this
large non-Parquet text file. It stops reading as soon as TARGET non-empty
lines have been collected, subject to MAX_BYTES safety cap.
"""
from __future__ import annotations
import hashlib, json, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "tamil" / "indiccorp_v2_tamil_pilot.txt"
META = ROOT / "metadata" / "indiccorp_v2_tamil_acquisition.json"
SOURCE_URL = "https://huggingface.co/datasets/ai4bharat/IndicCorpV2/resolve/main/data/ta.txt"
TARGET = 10_000
CHUNK_SIZE = 64 * 1024
MAX_BYTES = 64 * 1024 * 1024  # safety cap: stop rather than stream indefinitely

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        SOURCE_URL + "?download=true",
        headers={"User-Agent": "IGRIS-Corpus-Pilot/1.1", "Accept-Encoding": "identity"}
    )
    rows=[]
    pending=b""
    digest=hashlib.sha256()
    bytes_read=0
    content_length=None
    status=None
    try:
        response=urllib.request.urlopen(req, timeout=90)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"Source request failed with HTTP {exc.code}: {exc.reason}. "
            "No fallback to full-file download was attempted."
        ) from exc
    with response:
        status=getattr(response, "status", None)
        content_length=response.headers.get("Content-Length")
        while len(rows) < TARGET and bytes_read < MAX_BYTES:
            block=response.read(min(CHUNK_SIZE, MAX_BYTES-bytes_read))
            if not block:
                break
            bytes_read += len(block)
            digest.update(block)
            pending += block
            pieces=pending.split(b"\n")
            pending=pieces.pop()
            for raw in pieces:
                raw=raw.rstrip(b"\r")
                if not raw:
                    continue
                try:
                    line=raw.decode("utf-8", errors="strict")
                except UnicodeDecodeError as exc:
                    raise RuntimeError(
                        f"Invalid UTF-8 in source near byte {bytes_read-len(pending)}; "
                        "stopping without writing a corpus."
                    ) from exc
                rows.append(line)
                if len(rows) >= TARGET:
                    break
        # If EOF occurred, include final unterminated record.
        if len(rows) < TARGET and pending:
            try:
                line=pending.rstrip(b"\r").decode("utf-8", errors="strict")
            except UnicodeDecodeError as exc:
                raise RuntimeError("Final source record is not valid UTF-8.") from exc
            if line:
                rows.append(line)

    if len(rows) < TARGET:
        raise RuntimeError(
            f"Only {len(rows)} non-empty records collected within the "
            f"{MAX_BYTES:,}-byte safety cap / available source. "
            "No partial corpus was written. Review before changing limits."
        )

    # Write only after successful collection and strict UTF-8 decoding.
    data=("".join(x+"\n" for x in rows[:TARGET])).encode("utf-8")
    OUT.write_bytes(data)
    report={
        "dataset":"ai4bharat/IndicCorpV2",
        "dataset_url":"https://huggingface.co/datasets/ai4bharat/IndicCorpV2",
        "source_file":"data/ta.txt",
        "source_file_url":SOURCE_URL,
        "retrieval_method":"streaming raw text; early stop after first 10,000 non-empty lines",
        "http_status":status,
        "content_length_header":content_length,
        "target_records":TARGET,
        "records_saved":len(rows[:TARGET]),
        "bytes_read_from_source":bytes_read,
        "output":"data/raw/tamil/indiccorp_v2_tamil_pilot.txt",
        "output_bytes":len(data),
        "output_sha256":sha256_bytes(data),
        "source_prefix_sha256":digest.hexdigest(),
        "retrieval_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
        "declared_license":"CC0 per dataset card",
        "limitations":[
            "First 10,000 non-empty lines only; not random or representative.",
            "Partial-file hash is not the full source-file SHA-256.",
            "Dataset card's CC0 statement does not independently establish rights in every underlying source document.",
            "Review provenance and quality before commercial use.",
            "No tokenizer training was performed."
        ]
    }
    META.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
