# IGRIS 3B.51.18 — Tamil Pilot Acquisition

This separate kit fetches up to 10,000 rows from AI4Bharat IndicCorp V2 via the Hugging Face dataset viewer API. It uses Python standard library only and does not download the 11.8 GB raw Tamil file.

## Run (PowerShell)
Extract this kit, then enter the inner `igris_3b51_18_tamil_pilot_acquisition` folder:

```powershell
cd C:\IGRIS\igris_3b51_18_tamil_pilot_acquisition\igris_3b51_18_tamil_pilot_acquisition
& C:\IGRIS\.venv\Scripts\python.exe .\scripts\acquire_tamil_pilot.py
```

Output:
- `data\raw\tamil\indiccorp_v2_tamil_pilot.txt`
- `metadata\indiccorp_v2_tamil_acquisition.json`

The script uses the first 10,000 available rows, not a random sample. If the dataset viewer rejects the config/split or returns no rows, it stops rather than downloading the full file. After acquisition, run the v17 preparation script from its own folder by pointing/copying only this approved input into v17's `data\raw\tamil\` folder.

## Safety and scope
- No package installation.
- No modification to `C:\IGRIS` production repository or v16/v17 folders.
- No tokenizer training.
- The dataset card states CC0 for datasets created by the project, but this is not a blanket legal guarantee for every underlying web document. Commercial use still requires provenance and content review.
