import csv
import json
from pathlib import Path
import regex
from tokenizers import Tokenizer

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"

tok_a = Tokenizer.from_file(str(WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"))
tok_exp = Tokenizer.from_file(str(PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"))

with open(WORKSPACE_ROOT / "TOKENIZER_OWNER_REVIEW_30.csv", "r", encoding="utf-8") as f:
    rows_30 = list(csv.DictReader(f))

print(f"Loaded {len(rows_30)} rows from TOKENIZER_OWNER_REVIEW_30.csv")

for r in rows_30:
    text = r["original_text"]
    enc_a = tok_a.encode(text)
    enc_exp = tok_exp.encode(text)
    
    dec_a = tok_a.decode(enc_a.ids)
    dec_exp = tok_exp.decode(enc_exp.ids)
    
    rec_pass = (dec_a == text and dec_exp == text)
    print(f"{r['review_id']} [{r['language']}] {text!r}: IDs_A={enc_a.ids} vs IDs_Exp={enc_exp.ids} | RecPass={rec_pass}")
