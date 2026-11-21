# IGRIS 3B.51.21 — Source Recovery and Record Validation

## Scope
This kit checks whether truncated/flagged mixed-script previews can be recovered from the original immutable Tamil pilot text file.

It does NOT:
- download any data
- modify raw or classified inputs
- normalize or deduplicate records
- approve records for training
- perform tokenizer training

## Extract
Extract the ZIP. If there is a nested folder with the same name, enter the inner folder:
`C:\IGRIS\igris_3b51_21_source_recovery_validation\igris_3b51_21_source_recovery_validation`

Verify:
```powershell
Test-Path .\scripts\recover_source_records.py
```
Expected: `True`.

## Run
Use these exact paths if your folders match the earlier steps:
```powershell
& C:\IGRIS\.venv\Scripts\python.exe .\scripts\recover_source_records.py `
  --raw "C:\IGRIS\igris_3b51_18_1_tamil_pilot_acquisition_fix\igris_3b51_18_1_tamil_pilot_acquisition\data\raw\tamil\indiccorp_v2_tamil_pilot.txt" `
  --likely "C:\IGRIS\igris_3b51_20_1_mixed_script_classification\igris_3b51_20_1_mixed_script_classification\processed\mixed_script_classification\likely_valid.jsonl" `
  --contamination "C:\IGRIS\igris_3b51_20_1_mixed_script_classification\igris_3b51_20_1_mixed_script_classification\processed\mixed_script_classification\contamination_candidate.jsonl" `
  --ambiguous "C:\IGRIS\igris_3b51_20_1_mixed_script_classification\igris_3b51_20_1_mixed_script_classification\processed\mixed_script_classification\ambiguous.jsonl"
```

## Outputs
Under `processed\source_recovery\`:
- `source_recovery_report.json` — counts, hashes and status summary.
- `source_recovery_audit.jsonl` — all input records with source match results.
- `recovered_records.jsonl` — records whose source preview matched the raw line.
- `unresolved_records.jsonl` — mismatches, invalid references and unresolved cases.

## Important interpretation
The script assumes `original_record.line` is a 1-based line number in the raw source. It verifies the preview against the referenced raw line before accepting a recovery. If the source line numbering convention differs, records will be marked MISMATCH or out of range; do not change line offsets blindly. Share the report first.

A recovered full record is not automatically clean. It still needs quality, contamination, duplicate, and licensing review.
