# IGRIS Milestone 3B.52 — Production Tokenizer Integration Patch

This is a **separate, reviewable patch** based on the four uploaded IGRIS source modules. It does not modify your existing `C:\IGRIS` repository.

## Included

- `src/igris/tokenizer/strict.py`: strict Candidate A/B adapters, NFC/exact Unicode modes, sentinel escaping, strict ID validation, batch APIs, structural rendering, raw-byte codec, and artifact loaders.
- `src/igris/tokenizer/ingestion.py`: shared ingestion API. Public encoding does **not** add BOS/EOS automatically; framing is opt-in.
- `tests/test_contract.py`: contract tests using an explicitly labelled in-memory test double. These do not pretend to test trained tokenizer artifacts.
- `scripts/check_approved_inventory.py`: read-only check of the uploaded 42-line inventory.

## Requirements

Use the existing project virtual environment. No package installation is performed by this patch. Runtime dependencies for artifact loading are the already-approved packages:

- `tokenizers==0.23.3`
- `sentencepiece==0.2.3`
- `unicodedata2==15.1.0`

## Install into a test copy first

Copy the `src\igris\tokenizer` folder into your project `src\igris\` folder (or merge it into the equivalent package path). Do not overwrite your existing files. If `src\igris` is not your active import root, adjust `PYTHONPATH` accordingly.

From PowerShell:

```powershell
cd C:\IGRIS
$env:PYTHONPATH = (Join-Path (Get-Location) "src")
C:\IGRIS\.venv\Scripts\python.exe -m unittest discover -s .\igris_3b52_patch\tests -v
C:\IGRIS\.venv\Scripts\python.exe .\igris_3b52_patch\scripts\check_approved_inventory.py "C:\path\to\approved_line_inventory.csv"
```

If you extract the ZIP elsewhere, replace `igris_3b52_patch` with that extracted directory path. The test file adds its own patch `src` path, so the first command works without PYTHONPATH too.

## Artifact smoke tests (not run here)

Once genuine artifacts exist, load them explicitly:

```python
from igris.tokenizer import load_candidate_a, load_candidate_b
A = load_candidate_a(r"path\to\tokenizer.json")
B = load_candidate_b(r"path\to\tokenizer.model")
```

Both loaders enforce exactly 32,768 vocabulary entries, all 12 structural tokens at IDs 0–11, and a complete unique 256-byte mapping. A successful loader call still does not establish training-data rights or approve a corpus.

## Corpus inventory status

The supplied inventory is expected to contain 42 classification-only rows: 20 candidates pending cleanup/provenance and 22 excluded quarantine rows. The inventory checker validates those counts only. It intentionally does **not** mark any record training-eligible and does not launch training.

## Explicitly not performed

- No tokenizer training or corpus reading.
- No corpus cleanup, merge, deletion, or promotion.
- No model architecture changes.
- No downloads or package installations.
- No edits to the existing repository.

## Acceptance boundary

The included unit tests exercise wrapper contract behavior using a test double. Real Candidate A/B artifact acceptance, byte fallback behavior, actual save/reload fidelity, deterministic training, and performance remain **NOT TESTED** until trained artifacts are supplied and tested. Do not label this patch production-accepted until those artifact-level tests pass.
