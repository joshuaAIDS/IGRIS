# IGRIS 3B.51.23.6 — Tamil Review Register (read-only)

This package builds a human-review register for the 24 flagged Tamil corpus records.
It does not edit, delete, merge, normalize, quarantine, or promote any source record.

## Run on Windows PowerShell

From this extracted package folder:

```powershell
C:\IGRIS\.venv\Scripts\python.exe .\scripts\build_review_register.py `
  --clean "C:\IGRIS\igris_3b51_19_1_tamil_remediation\igris_3b51_19_1_tamil_remediation\processed\tamil_nfc_deduplicated.txt" `
  --flagged ".\reports\clean_flagged_records_review.jsonl" `
  --out ".\reports\stage2_review_register"
```

Copy `clean_flagged_records_review.jsonl` from your Stage 1 package into this package's
`reports` folder before running, or pass its full path to `--flagged`.

Outputs:
- `tamil_human_review_register.csv` — includes the full original source record.
- `tamil_human_review_register.jsonl` — same information in JSONL.
- `tamil_review_register_summary.json` — counts, hashes, and audit status.

All classifications are preliminary recommendations from the manual inspection in this
conversation. `human_approval_status` is always `PENDING`. The script checks source-line
references and records hashes; it does not make content decisions or change inputs.
