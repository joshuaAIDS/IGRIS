import json
from pathlib import Path

transcript_path = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102\.system_generated\logs\transcript.jsonl")

with open(transcript_path, encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "Tamil: 153" in line or "153" in line and "Tamil" in line and "Tanglish" in line:
            data = json.loads(line)
            print(f"Step {i}: type={data.get('type')}, source={data.get('source')}")
            c = data.get("content", "")
            t = data.get("thinking", "")
            if c:
                print(" Content match:", c[:150])
            if t and "153" in t:
                idx = t.find("153")
                print(" Thinking match:", t[idx-50:idx+150])
