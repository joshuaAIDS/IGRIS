IGRIS 3B.51.23.3 — Source Recovery Closure Audit
================================================

Purpose
-------
Read-only closure audit for the 10 unresolved source references, using:
- the original raw Tamil pilot TXT;
- unresolved_records.jsonl;
- source_recovery_report.json;
- deep_unresolved_investigation.json.

It verifies the raw source hash, checks source line references, validates
NFC equality for non-truncated previews and NFC-prefix correspondence for
records explicitly marked truncated, and writes full source lines to a
SEPARATE review-only JSONL file with original metadata retained.

It does NOT:
- modify any input;
- merge records into the cleaned corpus;
- change classifications;
- approve content quality, provenance, licensing, or commercial use;
- train a tokenizer or download data.

Extract into C:\IGRIS, then run from the inner folder:

python .\scripts\closure_audit.py `
  --raw "C:\IGRIS\igris_3b51_18_1_tamil_pilot_acquisition_fix\igris_3b51_18_1_tamil_pilot_acquisition\data\raw\tamil\indiccorp_v2_tamil_pilot.txt" `
  --unresolved "C:\IGRIS\igris_3b51_21_source_recovery_validation\igris_3b51_21_source_recovery_validation\processed\source_recovery\unresolved_records.jsonl" `
  --recovery-report "C:\IGRIS\igris_3b51_21_source_recovery_validation\igris_3b51_21_source_recovery_validation\processed\source_recovery\source_recovery_report.json" `
  --deep-report "C:\IGRIS\igris_3b51_23_2_deep_unresolved_investigation\igris_3b51_23_2_deep_unresolved_investigation\reports\deep_unresolved_investigation.json" `
  --out ".\reports"

Outputs:
- source_recovery_closure_report.json
- recovered_source_lines_review_only.jsonl

A PASS_WITH_REVIEW result means the source correspondence checks passed.
The recovered JSONL is a review artifact only and must not be treated as
training-ready or merged into the cleaned corpus without separate approval.
