# IGRIS 3B.53.3 — Synthetic backend loader validation

This kit creates temporary, synthetic Candidate A (ByteLevel BPE) and Candidate B (SentencePiece Unigram) fixtures and calls the integrated `load_candidate_a()` / `load_candidate_b()` functions. It does **not** train on the Tamil corpus, read corpus files, or create production tokenizer artifacts.

## Required layout

Extract this kit and the previously supplied `igris_3b53_2_full_integrated_code.zip` under `C:\IGRIS` so the integrated-code folder is:

`C:\IGRIS\igris_3b53_2_full_integrated_code\`

The script expects its own folder to contain a copy of `src\igris\tokenizer` from that integrated-code folder. Copy the folder if needed, or use the PowerShell commands below.

## PowerShell

```powershell
$kit = "C:\IGRIS\igris_3b53_3_synthetic_backend_validation"
$integrated = "C:\IGRIS\igris_3b53_2_full_integrated_code"
Copy-Item "$integrated\src\igris" "$kit\src\igris" -Recurse -Force
& "C:\IGRIS\.venv\Scripts\python.exe" "$kit\scripts\run_synthetic_backend_validation.py"
```

If your extracted kit has an extra nested directory, set `$kit` to the directory containing `scripts\run_synthetic_backend_validation.py`.

## Expected result

`PASS_SYNTHETIC_BACKEND_LOADERS`, with Candidate A and B each reporting loader, vocabulary, text round-trip, and raw-binary round-trip PASS.

A failure is useful diagnostic evidence. Do not modify the Tamil corpus or start tokenizer training to fix a fixture failure. Share the complete traceback/report first.
