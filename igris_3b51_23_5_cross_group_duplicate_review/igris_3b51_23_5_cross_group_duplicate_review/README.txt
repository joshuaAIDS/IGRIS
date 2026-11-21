IGRIS 3B.51.23.5 — Cross-Group Duplicate Review

Read-only classification of the 439 duplicate keys from the v3 consolidation
audit. It resolves row references against the four existing data files and
writes a review register plus summary. It does not edit inputs, remove
duplicates, merge groups, promote review-only records, approve licensing, or
train tokenizers.

Run from this extracted inner folder:

C:\IGRIS\.venv\Scripts\python.exe .\scripts\review_duplicates.py --help

Then use the full command supplied in chat. Expected known category counts
from the previous audit:
- clean;mixed: 427
- clean;recovered_review_only: 7
- clean;mixed;recovered_review_only: 3
- mixed;quarantine: 2

Policy:
- clean;mixed: mixed-script is an extra review label; not a reason by itself
  to remove an otherwise clean record.
- recovered overlaps: recovered copies remain review-only.
- mixed;quarantine: quarantine prevails. Keep both records quarantined.
No records are automatically changed.
