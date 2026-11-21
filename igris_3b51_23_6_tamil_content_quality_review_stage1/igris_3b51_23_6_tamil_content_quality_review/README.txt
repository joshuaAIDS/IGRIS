IGRIS 3B.51.23.6 — Tamil Content & Quality Review (Stage 1: Read-only profile)

This stage profiles the existing clean Tamil pilot and counts the mixed and
quarantine review files. It does not change any inputs, classify text as
approved, make licensing decisions, merge records, or train a tokenizer.

The script emits:
- tamil_content_quality_profile.json
- clean_flagged_records_review.jsonl
- clean_stratified_sample_review.jsonl

Flagged records and sample contain text previews. Treat them as potentially
sensitive source material; do not publish or share publicly.

Use the project's existing Python 3.11 virtual environment. No packages are
installed by this kit. unicodedata2 is used if already available; otherwise
the report states the standard library Unicode database version.

Run --help first, then use the full command provided in chat.
