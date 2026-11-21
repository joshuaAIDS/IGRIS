IGRIS Milestone 3B.53 — Backend Integration Preflight
=====================================================

Purpose
-------
Safely inventory the extracted 3B.52 patch and identify the exact Candidate A/B
adapter modules, without importing project code, changing files, installing
packages, downloading anything, reading corpus contents, or starting training.

This is a preflight, not a production acceptance test. It checks source layout,
declared dependencies, and likely adapter entry points using Python AST only.

Run from the extracted patch directory:
  C:\IGRIS\.venv\Scripts\python.exe .\scripts\preflight_backend.py

Or pass the patch root explicitly:
  C:\IGRIS\.venv\Scripts\python.exe .\scripts\preflight_backend.py "C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch"

It writes no files. Copy the JSON output back into the chat.

No training authorization is granted by this kit.
