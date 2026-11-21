import json
from pathlib import Path
from tokenizers import Tokenizer

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
cand_a_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
cand_exp_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"

tok_a = Tokenizer.from_file(str(cand_a_path))
tok_exp = Tokenizer.from_file(str(cand_exp_path))

print("Original Candidate A vocab size:    ", tok_a.get_vocab_size())
print("Experimental Candidate A vocab size:", tok_exp.get_vocab_size())

with open(cand_a_path, encoding="utf-8") as f:
    d_a = json.load(f)
with open(cand_exp_path, encoding="utf-8") as f:
    d_exp = json.load(f)

merges_a = d_a["model"].get("merges", [])
merges_exp = d_exp["model"].get("merges", [])

print(f"Original Candidate A merges count:    {len(merges_a)}")
print(f"Experimental Candidate A merges count:{len(merges_exp)}")

# Test sample encoding
sample_ta = "இக்ரிஸ் தமிழ் மொழியை எவ்வாறு புரிந்துகொள்கிறது?"
sample_en = "Explain how IGRIS handles trilingual tokenization with Candidate A."
sample_tg = "Microservice health checks pass ஆனா மட்டும் தான் traffic route ஆகும்."

enc_a_ta = tok_a.encode(sample_ta)
enc_exp_ta = tok_exp.encode(sample_ta)

enc_a_en = tok_a.encode(sample_en)
enc_exp_en = tok_exp.encode(sample_en)

enc_a_tg = tok_a.encode(sample_tg)
enc_exp_tg = tok_exp.encode(sample_tg)

print("\nTamil tokens:")
print("  Original A:    ", len(enc_a_ta.tokens), enc_a_ta.tokens[:10])
print("  Experimental A:", len(enc_exp_ta.tokens), enc_exp_ta.tokens[:10])

print("\nEnglish tokens:")
print("  Original A:    ", len(enc_a_en.tokens), enc_a_en.tokens[:10])
print("  Experimental A:", len(enc_exp_en.tokens), enc_exp_en.tokens[:10])

print("\nTanglish tokens:")
print("  Original A:    ", len(enc_a_tg.tokens), enc_a_tg.tokens[:10])
print("  Experimental A:", len(enc_exp_tg.tokens), enc_exp_tg.tokens[:10])
