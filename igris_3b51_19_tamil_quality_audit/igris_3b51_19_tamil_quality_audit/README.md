# IGRIS 3B.51.19 — Tamil Pilot Quality Audit

This is a **read-only** audit. It does not edit the corpus, download data,
install packages, modify the IGRIS repository, or train a tokenizer.

## Run from PowerShell

Extract this ZIP. Then run from the extracted kit directory:

```powershell
& C:\IGRIS\.venv\Scripts\python.exe .\scripts\audit_tamil_pilot.py --input "C:\IGRIS\igris_3b51_18_1_tamil_pilot_acquisition_fix\igris_3b51_18_1_tamil_pilot_acquisition\data\raw\tamil\indiccorp_v2_tamil_pilot.txt" --output ".\reports\tamil_quality_report.json"
```

If your extraction folder differs, adjust only the `--input` path. Confirm the file exists first:

```powershell
Test-Path "C:\IGRIS\igris_3b51_18_1_tamil_pilot_acquisition_fix\igris_3b51_18_1_tamil_pilot_acquisition\data\raw\tamil\indiccorp_v2_tamil_pilot.txt"
```

## Checks
- Strict UTF-8 decoding (fails closed; no replacement decoding)
- SHA-256 of the acquired file
- Total, blank and non-empty record counts
- Exact duplicate count
- NFC mismatch count
- Tamil-block, Latin-letter and other-script letter counts
- Records with Tamil, without Tamil, or mixing Tamil and Latin
- U+FFFD, NUL and control-character counts
- Record length min/median/p95/p99/max
- Occurrences of the 12 approved IGRIS structural spellings

## Important limitations
- This is a technical audit, not a semantic quality or legal-rights determination.
- A Tamil-block character count does not prove every record is Tamil or useful.
- Unicode database comes from the active Python runtime; it may not be Unicode 15.1.
- The audit does not normalize, deduplicate, delete or rewrite the source.
- Structural token occurrences are flags only; no escaping is applied.
- The first 10,000 source lines are not a random or representative sample.
