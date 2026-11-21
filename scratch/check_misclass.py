import json, sys
sys.path.insert(0, r'C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\scripts')
from language_identifier_v2 import LanguageIdentifierV2
lid = LanguageIdentifierV2()

with open(r'C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        cat = obj.get('category')
        res = lid.identify(obj['text'])
        if res.label != 'TANGLISH':
            print(f"[{cat}] ID={obj.get('id')} Pred={res.label} Conf={res.confidence}")
            print(f"  Text: {obj['text']}")
