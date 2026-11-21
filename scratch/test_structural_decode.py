from pathlib import Path
from tokenizers import Tokenizer

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
tok_a = Tokenizer.from_file(str(PATCH_ROOT / "artifacts/tokenizer/candidate_a/tokenizer.json"))
tok_exp = Tokenizer.from_file(str(PATCH_ROOT / "artifacts/tokenizer/candidate_a_synthetic_experiment/tokenizer.json"))

s = "<|user|> What is IGRIS? <|assistant|> <think> Analyzing </think>"
enc_a = tok_a.encode(s)
print("Default decode A:", repr(tok_a.decode(enc_a.ids)))
print("skip_special_tokens=False A:", repr(tok_a.decode(enc_a.ids, skip_special_tokens=False)))

enc_exp = tok_exp.encode(s)
print("Default decode Exp:", repr(tok_exp.decode(enc_exp.ids)))
print("skip_special_tokens=False Exp:", repr(tok_exp.decode(enc_exp.ids, skip_special_tokens=False)))

# Check token IDs for structural tokens
print("IDs A:", enc_a.ids)
print("IDs Exp:", enc_exp.ids)
print("Tokens A:", enc_a.tokens)
print("Tokens Exp:", enc_exp.tokens)
