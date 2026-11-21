import check_lang_labels

docs = {d["raw_id"]: d for d in check_lang_labels.unique_docs}
print(repr(docs["P25-SYN-0106"]["text"]))
