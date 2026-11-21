import csv
with open("TOKENIZER_FRAGMENTATION_ANALYSIS.csv") as f:
    for row in csv.DictReader(f):
        print(row["evaluation_scope"])
        print("  Cand A: TPW =", row["cand_a_tpw"], "| CPT =", row["cand_a_cpt"], "| Single-Token % =", row["cand_a_single_token_word_pct"], "| Excessive Frag % =", row["cand_a_excessive_fragmentation_pct"])
        print("  Cand Exp: TPW =", row["cand_exp_tpw"], "| CPT =", row["cand_exp_cpt"], "| Single-Token % =", row["cand_exp_single_token_word_pct"], "| Excessive Frag % =", row["cand_exp_excessive_fragmentation_pct"])
        print("  Token Reduction =", row["token_reduction_pct"], "% | UNK =", row["unknown_token_rate"], "| Roundtrip =", row["exact_roundtrip_accuracy"])
