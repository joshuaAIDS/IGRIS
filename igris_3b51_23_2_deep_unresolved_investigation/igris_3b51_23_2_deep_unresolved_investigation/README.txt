IGRIS 3B.51.23.2 — Deep Unresolved-Record Investigation
========================================================

Purpose
-------
Read-only diagnostic investigation of unresolved Tamil source records.
It compares saved previews against their referenced raw source lines and
produces detailed evidence for manual review.

It does NOT:
- modify the raw source, unresolved JSONL, or recovery report;
- repair or rewrite source records;
- approve records for corpus inclusion;
- download data or train a tokenizer.

Inputs
------
Use the same three inputs from 3B.51.23.1:
1. raw Tamil pilot TXT
2. unresolved_records.jsonl
3. source_recovery_report.json

Run from this extracted kit folder in PowerShell:

python .\scripts\deep_investigate.py `
  --raw "C:\IGRIS\igris_3b51_18_1_tamil_pilot_acquisition_fix\igris_3b51_18_1_tamil_pilot_acquisition\data\raw\tamil\indiccorp_v2_tamil_pilot.txt" `
  --unresolved "C:\IGRIS\igris_3b51_21_source_recovery_validation\igris_3b51_21_source_recovery_validation\processed\source_recovery\unresolved_records.jsonl" `
  --recovery-report "C:\IGRIS\igris_3b51_21_source_recovery_validation\igris_3b51_21_source_recovery_validation\processed\source_recovery\source_recovery_report.json" `
  --out ".\reports"

Outputs
-------
- deep_unresolved_investigation.json
- deep_unresolved_character_diff.csv

Interpretation
--------------
The report distinguishes exact match, NFC match, preview-prefix match,
and no match. Prefix matches are only considered for records explicitly
marked truncated. It also reports first differing character positions,
Unicode code points, UTF-8 byte-prefix similarity, and diagnostic
Latin-1/CP1252 mojibake candidates. Diagnostic candidates are never
written back or treated as recovered records.

A successful script run is not approval. Any NO_MATCH remains unresolved
until manually reviewed with source provenance and content-quality checks.
