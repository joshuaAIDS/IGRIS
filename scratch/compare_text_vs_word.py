import csv
from tokenizers import Tokenizer

tok_a = Tokenizer.from_file(r"C:\IGRIS\artifacts\tokenizer\candidate_a\tokenizer.json")
tok_exp = Tokenizer.from_file(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_a_synthetic_experiment\tokenizer.json")

with open(r"C:\IGRIS\TOKENIZER_HUMAN_REVIEW_SAMPLE.csv", "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

tot_tokens_a_text = sum(len(tok_a.encode(r["original_text"]).tokens) for r in rows)
tot_tokens_exp_text = sum(len(tok_exp.encode(r["original_text"]).tokens) for r in rows)

print(f"Whole text encoding tokens:")
print(f"  Cand A:   {tot_tokens_a_text}")
print(f"  Cand Exp: {tot_tokens_exp_text}")
print(f"  Reduction: {(tot_tokens_a_text - tot_tokens_exp_text) / tot_tokens_a_text * 100:.2f}%")

# Now let's check what was in TOKENIZER_FRAGMENTATION_ANALYSIS.csv:
# 3429 for Cand A, 1943 for Cand Exp
print(f"In TOKENIZER_FRAGMENTATION_ANALYSIS.csv: Cand A=3429, Cand Exp=1943")
