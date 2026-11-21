# IGRIS 3B.51.18.1 — Tamil Pilot Acquisition Fix

The earlier v18 script called the Hugging Face dataset-viewer `/rows` API.
That API currently supports datasets with Parquet exports; IndicCorpV2's Tamil
source is a large plain-text `data/ta.txt` file, so the viewer returned HTTP 501.
See Hugging Face dataset-viewer documentation and the IndicCorpV2 repository.

This corrected script streams the raw `data/ta.txt` file and stops after the
first 10,000 non-empty newline-delimited records. It has a 64 MiB safety cap
and writes no output if it cannot collect the full target. It does not use the
dataset-viewer API and does not download the full 11.8 GB file intentionally.

## Install / run
No new packages required. Extract this folder and run from its root:

```powershell
& C:\IGRIS\.venv\Scripts\python.exe .\scripts\acquire_tamil_pilot.py
```

Output:
- `data/raw/tamil/indiccorp_v2_tamil_pilot.txt`
- `metadata/indiccorp_v2_tamil_acquisition.json`

The first 10,000 lines are not a random or representative sample. The CC0
statement is the dataset creator's declared licence; review underlying
provenance before commercial use. No tokenizer training occurs.
