IGRIS 3B.51.23.4.1 — Tamil consolidation audit correction (v3)

This is a corrected, read-only audit script. It fixes the remediation report
field name to `mixed_tamil_latin_records_for_review` and explicitly requires
Unicode database 15.1.0 via the already-installed `unicodedata2` package.
It does not install packages, modify inputs, merge records, delete duplicates,
approve licensing/content, or train a tokenizer.

Extract the ZIP into C:\IGRIS and run from the inner folder:

python .\scripts\consolidation_audit.py --help

Then rerun the same full audit command used for v2, changing only the current
working directory to this v3 folder. Keep all six input paths unchanged.
Use `--out ".\reports"`.

Expected consistency correction:
mixed_jsonl_records = 723
remediation.mixed_tamil_latin_records_for_review = 723

The duplicate CSV remains a review list. The two mixed/quarantine overlaps
must remain quarantined unless a separately authorized content review decides
otherwise. No record is automatically removed or promoted.
