IGRIS — Milestone 3B.51.23.14
Derivative cleanup workflow preparation (fail-closed, preview-only)

1. Extract this ZIP.
2. Run --help first.
3. Run the preflight with the existing clean corpus path.
4. Expected current result: PREFLIGHT_BLOCKED_PENDING_GATES (all 20 rows remain pending).
5. This script only hashes/counts the source and writes a JSON preflight report.
   It does NOT edit the source, create a derivative, clean text, redact PII,
   delete records, merge records, or promote records.
6. A row can pass the gate only after documented license clearance AND a
   separate explicit cleanup authorization are entered as APPROVED in the
   manifest. Do not change statuses without evidence and user approval.
7. Even when all gates pass, a separate implementation/review approval is
   required before any derivative corpus is generated.

No license is cleared by approval of the cleanup plan.
No tokenizer training is authorized.
