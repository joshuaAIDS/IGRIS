# IGRIS 3B.51.23.1 — Tamil audit correction

This corrected, read-only utility addresses the actual nested JSONL structure:
`original_classification_record.original_record.text`.

It checks the original 10 unresolved records against their 1-based raw source line references. It compares exact text, NFC-equivalent text, and diagnostic mojibake-repaired text. For explicitly truncated records, it also checks whether the saved preview is a prefix of the source line.

Mojibake repair is diagnostic only. It never modifies the source or JSONL files and never silently rewrites records.

## Run from the extracted folder

```powershell
py .\scripts\reconcile_unresolved.py `
  --raw "C:\IGRIS\igris_3b51_18_1_tamil_pilot_acquisition_fix\igris_3b51_18_1_tamil_pilot_acquisition\data\raw\tamil\indiccorp_v2_tamil_pilot.txt" `
  --unresolved "C:\IGRIS\igris_3b51_21_source_recovery_validation\igris_3b51_21_source_recovery_validation\processed\source_recovery\unresolved_records.jsonl" `
  --recovery-report "C:\IGRIS\igris_3b51_21_source_recovery_validation\igris_3b51_21_source_recovery_validation\processed\source_recovery\source_recovery_report.json" `
  --out ".\reconciliation_output"
```

Outputs:
- `tamil_source_reconciliation_report.json`
- `unresolved_case_comparison.csv`

Status is diagnostic, not dataset approval. No training, downloads, or repository edits.


v2 correction: source-prefix matching is permitted only for records explicitly marked truncated. Do not use the earlier v1 script for the final reconciliation.
