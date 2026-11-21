import json

with open(r'C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        idx = obj.get('step_index', 0)
        if 5860 <= idx <= 5890:
            calls = [c.get('name') for c in obj.get('tool_calls', [])]
            print(f"Step {idx}: type={obj.get('type')} status={obj.get('status')} calls={calls}")
            if obj.get('thinking'):
                print("Thinking preview:", obj.get('thinking')[:150].replace('\n', ' '))
