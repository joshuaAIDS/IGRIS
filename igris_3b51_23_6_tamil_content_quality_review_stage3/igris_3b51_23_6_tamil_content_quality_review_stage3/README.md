# IGRIS Stage 3 — Tamil Content & Quality Audit

Read-only profiling and heuristic flagging. No source edits, deletion, merging, dataset approval, licensing approval, downloads, or tokenizer training.

Requires the existing IGRIS venv with `unicodedata2` (Unicode 15.1) and `regex`. No installation is requested.

Extract the ZIP; it may create a nested same-name folder. Locate the script:
```powershell
Get-ChildItem "C:\IGRIS\igris_3b_51_23_6_tamil_content_quality_review_stage3" -Recurse -Filter audit_tamil_stage3.py
```

Run from the directory containing `scripts`:
```powershell
C:\IGRIS\.venv\Scripts\python.exe .\scripts\audit_tamil_stage3.py `
  --clean "C:\IGRIS\igris_3b_51_19_1_tamil_remediation\igris_3b_51_19_1_tamil_remediation\processed\tamil_nfc_deduplicated.txt" `
  --review-register "C:\IGRIS\igris_3b_51_23_6_tamil_review_register\igris_3b_51_23_6_tamil_review_register\reports\stage2_review_register\tamil_human_review_register.csv" `
  --out ".\reports\stage3"
```

Outputs:
- `tamil_stage3_quality_audit.json`
- `tamil_stage3_flagged_records.csv`

The CSV contains source line numbers, flag reasons, and character lengths, not record contents. Flags require human review; they are not automatic rejection decisions.
