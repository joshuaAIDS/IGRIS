IGRIS 3B.51.23.4 — Tamil Corpus Consolidation Audit
====================================================

READ-ONLY INVENTORY / DUPLICATE / INTEGRITY AUDIT
This kit does NOT merge datasets, modify source files, approve content,
approve licensing, or train a tokenizer.

Inputs expected:
1) Clean Tamil TXT (one record per line)
2) Mixed-script review JSONL
3) Quarantine JSONL
4) Recovered source-lines review-only JSONL
5) Tamil remediation report JSON
6) Source recovery closure report JSON

Extract into C:\IGRIS, then run from the inner folder:

python .\scripts\consolidation_audit.py `
  --clean "C:\IGRIS\igris_3b51_19_1_tamil_remediation\igris_3b51_19_1_tamil_remediation\processed\tamil_nfc_deduplicated.txt" `
  --mixed "C:\IGRIS\igris_3b51_19_1_tamil_remediation\igris_3b51_19_1_tamil_remediation\processed\tamil_mixed_script_review.jsonl" `
  --quarantine "C:\IGRIS\igris_3b51_19_1_tamil_remediation\igris_3b51_19_1_tamil_remediation\processed\tamil_quarantine.jsonl" `
  --recovered "C:\IGRIS\igris_3b51_23_3_source_recovery_closure_audit\igris_3b51_23_3_source_recovery_closure_audit\reports\recovered_source_lines_review_only.jsonl" `
  --remediation-report "C:\IGRIS\igris_3b51_19_1_tamil_remediation\igris_3b51_19_1_tamil_remediation\reports\tamil_remediation_report.json" `
  --closure-report "C:\IGRIS\igris_3b51_23_3_source_recovery_closure_audit\igris_3b51_23_3_source_recovery_closure_audit\reports\source_recovery_closure_report.json" `
  --out ".\reports"

Outputs:
- tamil_consolidation_audit.json
- cross_group_duplicate_candidates.csv

The audit computes byte hashes, line/record counts, NFC-normalized exact
duplicate candidates across groups, and consistency checks against the
remediation and closure reports. JSONL text extraction is conservative:
it checks common text fields and nested original-record fields. Any record
without a recognized text field is counted as text_unresolved, not silently
discarded.

Important:
- A duplicate candidate is not automatically deleted.
- The mixed-script group remains review-only.
- Quarantine remains quarantined.
- Recovered source lines remain review-only and are not added to clean data.
- This audit does not inspect semantic quality, source rights, attribution,
  or commercial licensing.
