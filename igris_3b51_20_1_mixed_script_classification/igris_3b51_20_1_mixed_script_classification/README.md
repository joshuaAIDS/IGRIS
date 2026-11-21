# IGRIS 3B.51.20.1 — Mixed-script classification kit

## Purpose
A conservative, local-only review utility for the 723-record Tamil/Latin mixed-script JSONL file.

## Safety and scope
- Does not download data.
- Does not train a tokenizer.
- Does not modify the source JSONL.
- Does not delete records.
- Produces three heuristic review buckets plus a complete preserved copy.
- Classification is not a licensing decision or a definitive judgment of whether text is valid Tanglish.

## Extract
Extract the ZIP. If it creates a nested same-name folder, enter the inner folder:
`C:\IGRIS\igris_3b51_20_1_mixed_script_classification\igris_3b51_20_1_mixed_script_classification`

Check:
```powershell
Test-Path .\scripts\classify_mixed_script.py
```
It should return `True`.

## Run
Use the actual path to your uploaded/review file:
```powershell
& C:\IGRIS\.venv\Scripts\python.exe .\scripts\classify_mixed_script.py --input "C:\IGRIS\igris_3b51_19_1_tamil_remediation\igris_3b51_19_1_tamil_remediation\processed\tamil_mixed_script_review.jsonl"
```

## Outputs
Created under `processed\mixed_script_classification\`:
- `all_records_preserved.jsonl` — every non-empty source line preserved.
- `likely_valid.jsonl` — Tamil + Latin without strong contamination indicators.
- `contamination_candidate.jsonl` — HTML/script/SEO/navigation indicators.
- `ambiguous.jsonl` — URLs, structural-token-like text, or unclear cases.
- `mixed_script_classification_report.json` — counts, input SHA-256, and policy notes.

## Interpretation
The classifier uses conservative regular-expression indicators. False positives and false negatives are possible. Inspect samples from every bucket before deciding corpus inclusion. In particular, proper names, URLs cited as content, scientific names, abbreviations, and technical vocabulary may be legitimate. Do not start tokenizer training based only on this report.
