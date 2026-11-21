# IGRIS 3B.53.2 — Full integrated tokenizer code

This ZIP contains two complete Python source files:
- `src/igris/tokenizer/strict.py` — complete strict adapter with the new validators wired into both loaders.
- `src/igris/tokenizer/artifact_validation.py` — Candidate A/B serialized-artifact configuration checks.

## Install into the separate 3B.52 patch folder
Copy both files into:
`C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\src\igris\tokenizer\`

Overwrite the existing `strict.py` in that PATCH folder only, and add `artifact_validation.py`.
Do not copy into the production `C:\IGRIS\src` tree.

The existing `__init__.py` imports from `.strict`; it does not need changes.

## Verify syntax and existing wrapper tests
```powershell
C:\IGRIS\.venv\Scripts\python.exe -m compileall "C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\src\igris\tokenizer"
C:\IGRIS\.venv\Scripts\python.exe "C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\tests\test_contract.py"
```

These tests are not real tokenizer artifact acceptance. No real tokenizer artifacts exist yet.
No training, corpus reading, downloading, package installation, or production-repository modification is performed or authorized by this patch.
