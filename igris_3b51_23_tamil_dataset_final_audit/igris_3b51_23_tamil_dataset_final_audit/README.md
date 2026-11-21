# IGRIS 3B.51.23 — Consolidated Tamil Dataset Audit

Read-only audit kit. It does not train a tokenizer, download data, or modify source files.

## Required inputs
Pass paths to:
1. original Tamil pilot TXT
2. NFC/deduplicated clean TXT
3. quarantine JSONL
4. mixed-script review JSONL
5. recovered records JSONL
6. unresolved records JSONL
7. remediation report JSON
8. source recovery report JSON

The script checks hashes against the reports, counts records, validates UTF-8/NFC, compares unresolved records to source lines after NFC, and emits a consolidated report and summary CSV.

## Run on Windows PowerShell
Extract the ZIP, then run:

```powershell
py .\scripts\run_tamil_audit.py `
  --raw "C:\path\to\indicorp_v2_tamil_pilot.txt" `
  --clean "C:\path\to\tamil_nfc_deduplicated.txt" `
  --quarantine "C:\path\to\tamil_quarantine.jsonl" `
  --mixed "C:\path\to\tamil_mixed_script_review.jsonl" `
  --recovered "C:\path\to\recovered_records.jsonl" `
  --unresolved "C:\path\to\unresolved_records.jsonl" `
  --remediation-report "C:\path\to\tamil_remediation_report.json" `
  --recovery-report "C:\path\to\source_recovery_report.json" `
  --out ".\audit_output"
```

## Status rules
- `PASS`: all required files present, hashes/counts consistent, unresolved records reconcile, no technical blockers.
- `PASS_WITH_REVIEW`: technical checks pass but content, mixed-script, quarantine, provenance, or licensing review remains.
- `BLOCKED`: missing inputs, hash mismatch, invalid UTF-8, or unresolved source mismatch.

`approved_records.txt` is produced only when the raw source hash matches the recovery report and all source reconciliation checks pass. It is a technical candidate, not a commercial/licensing approval. Mixed-script records are not silently removed.
