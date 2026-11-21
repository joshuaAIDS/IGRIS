IGRIS Tamil 42-record approval + read-only audit

1. Extract this ZIP.
2. Edit the consolidated CSV register and set human_approval_status to
   APPROVED_CLASSIFICATION_ONLY for all 42 rows. Keep each existing
   recommended_classification unchanged.
3. Run the script against the original clean corpus and the approved CSV.

Example PowerShell (adjust paths if your extracted folders differ):

C:\IGRIS\.venv\Scripts\python.exe .\scripts\approval_readonly_audit.py `
  --clean "C:\IGRIS\igris_3b51_19_1_tamil_remediation\igris_3b51_19_1_tamil_remediation\processed\tamil_nfc_deduplicated.txt" `
  --register "C:\IGRIS\igris_tamil_42_record_consolidated_review_register\tamil_42_record_consolidated_review_register.csv" `
  --out ".\reports\approval_audit"

Expected counts:
- 42 approved classifications
- 20 KEEP_WITH_CLEANUP_REVIEW (still require cleanup/provenance review)
- 22 QUARANTINE_REVIEW (remain excluded)

This is read-only. It writes only reports to the chosen output folder.
It does not modify corpus files, delete records, merge records, approve
dataset licensing, or train a tokenizer/model.
