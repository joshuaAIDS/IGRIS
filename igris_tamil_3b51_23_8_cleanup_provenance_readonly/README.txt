IGRIS Milestone 3B.51.23.8 — Tamil Cleanup & Provenance Review (READ-ONLY)

Run with the approved register and unchanged clean corpus:

C:\IGRIS\.venv\Scripts\python.exe .\scripts\build_cleanup_provenance_manifest.py `
  --clean "C:\IGRIS\igris_3b51_19_1_tamil_remediation\igris_3b51_19_1_tamil_remediation\processed\tamil_nfc_deduplicated.txt" `
  --register "C:\IGRIS\igris_tamil_42_approved_classification_register\tamil_42_record_consolidated_review_register_APPROVED.csv" `
  --out ".\reports\cleanup_provenance_review"

Expected: 20 keep candidates manifested, 22 quarantine rows counted, source hash unchanged.
Outputs: cleanup_provenance_audit.json, cleanup_provenance_manifest.csv, cleanup_provenance_manifest.json.

The script only reads source files and writes reports. It does not edit/normalize/redact/delete/merge/promote corpus records.
Automated flags are heuristics. Source provenance and licensing cannot be proven from the text file; these require source-level evidence.
No tokenizer training is performed or authorized by this kit.
