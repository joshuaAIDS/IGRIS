#!/usr/bin/env python3
"""Fetch up to 10,000 Tamil rows from the Hugging Face dataset viewer API.

Uses Python standard library only. Does not download the 11.8 GB source file.
"""
from __future__ import annotations
import hashlib, json, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "tamil" / "indiccorp_v2_tamil_pilot.txt"
META = ROOT / "metadata" / "indiccorp_v2_tamil_acquisition.json"
DATASET = "ai4bharat/IndicCorpV2"
CONFIG = "indiccorp_v2"
SPLIT = "tam_Taml"
TARGET = 10_000
BATCH = 100
BASE = "https://datasets-server.huggingface.co/rows"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def fetch(offset: int, length: int) -> dict:
    params = urllib.parse.urlencode({
        "dataset": DATASET, "config": CONFIG, "split": SPLIT,
        "offset": offset, "length": length
    })
    req = urllib.request.Request(
        BASE + "?" + params,
        headers={"User-Agent": "IGRIS-Corpus-Pilot/1.0"}
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    offset = 0
    total_seen = 0
    failures = []
    while len(lines) < TARGET:
        length = min(BATCH, TARGET - len(lines))
        try:
            payload = fetch(offset, length)
            rows = payload.get("rows", [])
            if not rows:
                break
            for item in rows:
                row = item.get("row", {})
                value = row.get("text")
                if isinstance(value, str) and value.strip():
                    lines.append(value.rstrip("\r\n"))
                    if len(lines) >= TARGET:
                        break
            got = len(rows)
            total_seen += got
            offset += got
            if got < length:
                break
            time.sleep(0.25)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            failures.append({"offset": offset, "error": str(exc)})
            if len(failures) >= 3:
                raise RuntimeError(f"Stopped after 3 request failures: {failures}") from exc
            time.sleep(2)

    if not lines:
        raise RuntimeError(
            "No rows returned. The viewer may not expose this split/config; "
            "do not switch to downloading the 11.8 GB raw file automatically."
        )

    # Write exact returned text as UTF-8; v17 pipeline will apply NFC and dedup.
    OUT.write_text("".join(x + "\n" for x in lines), encoding="utf-8", newline="\n")
    report = {
        "dataset": DATASET,
        "dataset_url": "https://huggingface.co/datasets/ai4bharat/IndicCorpV2",
        "viewer_api": BASE,
        "config": CONFIG,
        "split": SPLIT,
        "target_records": TARGET,
        "records_saved": len(lines),
        "rows_returned_by_api": total_seen,
        "output": str(OUT.relative_to(ROOT)),
        "output_bytes": OUT.stat().st_size,
        "output_sha256": sha256(OUT),
        "declared_license": "CC0 per dataset card",
        "retrieval_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "request_failures": failures,
        "limitations": [
            "This is a first-N-row pilot sample, not a random or representative sample.",
            "Dataset card's CC0 statement does not independently establish rights in every underlying web document.",
            "Review source provenance and content before commercial use.",
            "No tokenizer training was performed."
        ]
    }
    META.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
