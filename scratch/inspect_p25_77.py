import check_lang_labels

docs = {d["raw_id"]: d for d in check_lang_labels.unique_docs}
for rid in ["P25-SYN-0077", "P26-VAL-0056", "syn_rec_000009"]:
    if rid in docs:
        d = docs[rid]
        print(rid, "text:", repr(d["text"]), "hint:", d["lang_hint"], "assigned:", d["assigned_lang"])
