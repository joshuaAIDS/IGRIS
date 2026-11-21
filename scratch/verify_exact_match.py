import check_lang_labels
from collections import Counter

docs = check_lang_labels.unique_docs
tanglish_docs = [d for d in docs if d["assigned_lang"] == "TANGLISH"]

p25_tg = [d for d in tanglish_docs if d["source_file"] == "PHASE25_SYNTHETIC_BENCHMARK_FIXTURES.jsonl"]
p26_tg = [d for d in tanglish_docs if d["source_file"] == "PHASE26_DATASET_SPLITS.json"]
p17_tg = [d for d in tanglish_docs if d["source_file"] == "igris_phase17_synthetic_multilingual.json"]
p23_tg = [d for d in tanglish_docs if d["source_file"] == "PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl"]
v2_tg = [d for d in tanglish_docs if d["source_file"] == "tanglish_synthetic_generator_v2.py"]

p25_ta = [d for d in p25_tg if any(0x0B80 <= ord(c) <= 0x0BFF for c in d["text"])]
p25_lat = [d for d in p25_tg if not any(0x0B80 <= ord(c) <= 0x0BFF for c in d["text"])]

p26_ta = [d for d in p26_tg if any(0x0B80 <= ord(c) <= 0x0BFF for c in d["text"])]
p26_lat = [d for d in p26_tg if not any(0x0B80 <= ord(c) <= 0x0BFF for c in d["text"])]

p17_ta = [d for d in p17_tg if any(0x0B80 <= ord(c) <= 0x0BFF for c in d["text"])]
p17_lat = [d for d in p17_tg if not any(0x0B80 <= ord(c) <= 0x0BFF for c in d["text"])]

print(f"P25: ta={len(p25_ta)}, lat={len(p25_lat)}, total={len(p25_tg)}")
print(f"P26: ta={len(p26_ta)}, lat={len(p26_lat)}, total={len(p26_tg)}")
print(f"P17: ta={len(p17_ta)}, lat={len(p17_lat)}, total={len(p17_tg)}")
print(f"P23: total={len(p23_tg)}")
print(f"V2:  total={len(v2_tg)}")

total_shift_to_ta = len(p25_ta) + len(p26_ta) + len(p17_ta)
total_shift_to_en = len(p25_lat) + len(p26_lat) + len(p17_lat)
total_remain_tg = len(p23_tg) + len(v2_tg)

print(f"\nTotal shifting from Tanglish to Tamil:   {total_shift_to_ta}")
print(f"Total shifting from Tanglish to English: {total_shift_to_en}")
print(f"Total remaining in Tanglish:            {total_remain_tg}")

orig_tamil = sum(1 for d in docs if d["assigned_lang"] == "TAMIL")
orig_english = sum(1 for d in docs if d["assigned_lang"] == "ENGLISH")
orig_tanglish = sum(1 for d in docs if d["assigned_lang"] == "TANGLISH")

print(f"\nOriginal: Tamil={orig_tamil}, English={orig_english}, Tanglish={orig_tanglish}")
print(f"Revised:  Tamil={orig_tamil + total_shift_to_ta}, English={orig_english + total_shift_to_en}, Tanglish={total_remain_tg}")
