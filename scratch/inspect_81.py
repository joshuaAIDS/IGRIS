import check_lang_labels

docs = check_lang_labels.unique_docs
tanglish_docs = [d for d in docs if d["assigned_lang"] == "TANGLISH"]
p25_p26_p17_tg = [d for d in tanglish_docs if d["source_file"] in ("PHASE25_SYNTHETIC_BENCHMARK_FIXTURES.jsonl", "PHASE26_DATASET_SPLITS.json", "igris_phase17_synthetic_multilingual.json")]

print(f"Total Tanglish in P25, P26, P17: {len(p25_p26_p17_tg)}")

# Let's inspect each of these 81 records
for i, d in enumerate(p25_p26_p17_tg):
    t = d["text"]
    has_ta_script = any(0x0B80 <= ord(c) <= 0x0BFF for c in t)
    # Check English stop words vs Tamil particles
    en_words = sum(1 for w in t.lower().split() if w in {"the", "is", "and", "in", "it", "to", "of", "for", "with", "on", "that", "this", "are", "from", "at", "as", "by", "an", "be", "was", "have", "has", "not", "but", "all", "they", "we", "can", "will", "one", "you", "did", "before", "without", "looks", "completely", "now", "no", "our", "someone", "please", "after"})
    ta_particles = sum(1 for w in t.lower().split() if w in {"da", "pa", "machan", "dei", "seri", "aiyoo", "aiyo", "thambi", "romba"})
    total_words = len(t.split())
    print(f"[{i+1:02d}] {d['source_file'][:8]} {d['raw_id']} | TaScript={has_ta_script} | EnWords={en_words}/{total_words} | TaPart={ta_particles} | {repr(t[:45])}")
