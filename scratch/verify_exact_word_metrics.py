import csv
from tokenizers import Tokenizer

tok_a = Tokenizer.from_file(r"C:\IGRIS\artifacts\tokenizer\candidate_a\tokenizer.json")
tok_exp = Tokenizer.from_file(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_a_synthetic_experiment\tokenizer.json")

with open(r"C:\IGRIS\TOKENIZER_HUMAN_REVIEW_SAMPLE.csv", "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# Let's verify word-level token counts
# When tokenizing individual words vs tokenizing whole text
def evaluate_partitions(rows):
    partitions = {
        "ENTIRE_EVALUATION_CORPUS": rows,
        "LANGUAGE_TAMIL": [r for r in rows if r["language"] == "TAMIL"],
        "LANGUAGE_ENGLISH": [r for r in rows if r["language"] == "ENGLISH"],
        "LANGUAGE_TANGLISH": [r for r in rows if r["language"] == "TANGLISH"],
    }
    
    for name, p_rows in partitions.items():
        all_words = []
        for r in p_rows:
            all_words.extend(r["original_text"].split())
            
        cand_a_tokens_list = [tok_a.encode(w).tokens for w in all_words]
        cand_exp_tokens_list = [tok_exp.encode(w).tokens for w in all_words]
        
        n_words = len(all_words)
        n_chars = sum(len(w) for w in all_words)
        
        tot_tok_a = sum(len(t) for t in cand_a_tokens_list)
        tot_tok_exp = sum(len(t) for t in cand_exp_tokens_list)
        
        fert_a = tot_tok_a / n_words
        fert_exp = tot_tok_exp / n_words
        
        cpt_a = n_chars / tot_tok_a
        cpt_exp = n_chars / tot_tok_exp
        
        single_a = sum(1 for t in cand_a_tokens_list if len(t) == 1) / n_words * 100
        single_exp = sum(1 for t in cand_exp_tokens_list if len(t) == 1) / n_words * 100
        
        frag_a = sum(1 for t in cand_a_tokens_list if len(t) > 1) / n_words * 100
        frag_exp = sum(1 for t in cand_exp_tokens_list if len(t) > 1) / n_words * 100
        
        excess_a = sum(1 for t in cand_a_tokens_list if len(t) >= 5) / n_words * 100
        excess_exp = sum(1 for t in cand_exp_tokens_list if len(t) >= 5) / n_words * 100
        
        tok_red = (tot_tok_a - tot_tok_exp) / tot_tok_a * 100
        
        print(f"=== {name} ===")
        print(f"  Words: {n_words}, Chars: {n_chars}")
        print(f"  Cand A:   Tokens={tot_tok_a}, Fert={fert_a:.4f}, CPT={cpt_a:.4f}, Single={single_a:.2f}%, Excess={excess_a:.2f}%")
        print(f"  Cand Exp: Tokens={tot_tok_exp}, Fert={fert_exp:.4f}, CPT={cpt_exp:.4f}, Single={single_exp:.2f}%, Excess={excess_exp:.2f}%")
        print(f"  Reduction: {tok_red:.2f}%")

evaluate_partitions(rows)
