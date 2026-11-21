import os
import re
from pathlib import Path

WORKSPACE = Path(r"C:\IGRIS")
ARTIFACTS = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")

targets = [WORKSPACE, ARTIFACTS]

pattern = re.compile(r"153.*131.*115|153.*Tamil|Tamil.*153|Tamil:\s*153|Tanglish:\s*115|English:\s*131", re.IGNORECASE)

matches = []

for base in targets:
    for root, dirs, files in os.walk(base):
        if ".git" in root or ".venv" in root:
            continue
        for file in files:
            if file.endswith((".py", ".md", ".csv", ".json", ".txt")):
                p = Path(root) / file
                try:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                    if "153" in text and ("131" in text or "115" in text):
                        matches.append(p)
                except Exception:
                    pass

print("Files matching 153 and (131 or 115):")
for m in set(matches):
    print(" ", m)
