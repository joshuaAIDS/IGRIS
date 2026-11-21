import json
from pathlib import Path

p = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_a\tokenizer.json")
data = json.loads(p.read_text(encoding="utf-8"))
vocab = data.get("model", {}).get("vocab", {})

# Sort by id
sorted_vocab = sorted(vocab.items(), key=lambda x: x[1])
print("First 15 tokens in Candidate A:")
for token, tid in sorted_vocab[:15]:
    print(f"  ID {tid}: {token}")
