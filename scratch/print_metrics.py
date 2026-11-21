import compute_all_metrics as m

print("\n--- Language Subsets ---")
for r in m.res_langs:
    print(f"{r['subset_name']:36s} N={r['record_count']:3d} Words={r['words_total']:5d} A_Fert={r['cand_a_fertility_per_word']:6.2f} Exp_Fert={r['cand_exp_fertility_per_word']:6.2f} Red={r['token_reduction_pct']:5.1f}% A_Vocab={r['cand_a_active_vocab_count']:3d} Exp_Vocab={r['cand_exp_active_vocab_count']:3d}")

print("\n--- Script Subsets ---")
for r in m.res_scripts:
    print(f"{r['subset_name']:36s} N={r['record_count']:3d} Words={r['words_total']:5d} A_Fert={r['cand_a_fertility_per_word']:6.2f} Exp_Fert={r['cand_exp_fertility_per_word']:6.2f} Red={r['token_reduction_pct']:5.1f}% A_Vocab={r['cand_a_active_vocab_count']:3d} Exp_Vocab={r['cand_exp_active_vocab_count']:3d}")
