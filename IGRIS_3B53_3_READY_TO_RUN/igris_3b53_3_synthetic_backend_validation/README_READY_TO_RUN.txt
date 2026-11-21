IGRIS 3B.53.3 — READY-TO-RUN SYNTHETIC BACKEND VALIDATION

This bundle already contains the corrected synthetic runner and corrected artifact validator.
It is self-contained; do not copy files from another ZIP.

1. Extract this ZIP to C:\IGRIS\igris_3b53_3_synthetic_backend_validation
2. Open PowerShell and run:

& "C:\IGRIS\.venv\Scripts\python.exe" "C:\IGRIS\igris_3b53_3_synthetic_backend_validation\scripts\run_synthetic_backend_validation.py"

If extracted into a nested folder, use the actual path to scripts\run_synthetic_backend_validation.py.

The script imports the included src\igris package. It creates temporary synthetic artifacts only.
It does not read the Tamil corpus, train tokenizers, or create production artifacts.

Expected success status: PASS_SYNTHETIC_BACKEND_LOADERS.
