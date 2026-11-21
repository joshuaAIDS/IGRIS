# IGRIS 3B.51.19.1 — Tamil remediation and Unicode 15.1 verification

This kit reads the original pilot file and never modifies it. It requires the already-installed
`unicodedata2==15.1.0`; it does not install packages, download data, or train a tokenizer.

## Run (PowerShell)
From this extracted kit's inner folder:
```powershell
& C:\IGRIS\.venv\Scripts\python.exe .\scripts\remediate_tamil.py --input "C:\IGRIS\igris_3b51_18_1_tamil_pilot_acquisition_fix\igris_3b51_18_1_tamil_pilot_acquisition\data\raw\tamil\indiccorp_v2_tamil_pilot.txt"
```

Outputs are written under `processed/` and `reports/` beside the script.

## Handling policy
- NFC-normalize each record using Unicode 15.1.
- Deduplicate after NFC using exact string equality; retain first occurrence.
- Keep mixed Tamil/Latin records in the processed output and flag them for review.
- Quarantine records containing U+FFFD, NUL, or control characters other than tab.
- Quarantine records exceeding 4,000 Unicode code points for manual review (this is a conservative pilot threshold, not a tokenizer limit).
- Flag structural-token spellings for review; do not silently escape or rewrite them.
- Preserve all original records by leaving the input untouched. Quarantine and review files are separate outputs.

The script does not certify dataset licensing, semantic quality, or commercial rights.
