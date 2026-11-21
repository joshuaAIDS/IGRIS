import os
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
for root, dirs, files in os.walk(PATCH_ROOT):
    for f in files:
        if f.endswith((".py", ".json", ".md", ".csv", ".txt")):
            p = Path(root) / f
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
                if "153" in txt:
                    print(f"Found '153' in: {p}")
            except Exception:
                pass
