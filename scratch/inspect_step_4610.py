import json
from pathlib import Path

transcript_path = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102\.system_generated\logs\transcript.jsonl")

with open(transcript_path, encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "Tamil: 153" in line:
            print(f"Line {i} has 'Tamil: 153'")
            data = json.loads(line)
            print("Keys:", list(data.keys()))
            print("Type:", data.get("type"))
            print("Content:", repr(data.get("content"))[:200])
