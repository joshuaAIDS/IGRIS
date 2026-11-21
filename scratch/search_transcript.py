import json
from pathlib import Path

transcript_path = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102\.system_generated\logs\transcript.jsonl")

with open(transcript_path, encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "153" in line and "131" in line:
            print(f"Match on line {i}")
            data = json.loads(line)
            # print snippet of content or thinking
            content = data.get("content", "")
            thinking = data.get("thinking", "")
            print("Content snippet:", content[:300] if content else "None")
            if "153" in thinking:
                print("Thinking snippet:", thinking[thinking.find("153")-100:thinking.find("153")+200])
