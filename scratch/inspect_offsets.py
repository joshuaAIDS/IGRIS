from tokenizers import Tokenizer

tok = Tokenizer.from_file('artifacts/tokenizer/candidate_a/tokenizer.json')

text = 'deploy பண்ணினோம்'
enc = tok.encode(text)

print("Original text:", text)
print("Tokens:", enc.tokens)
print("IDs:", enc.ids)
print("Offsets:", enc.offsets)
for i, (tok_str, (s, e)) in enumerate(zip(enc.tokens, enc.offsets)):
    print(f"[{i}] id={enc.ids[i]} piece={tok_str!r} offsets=({s}, {e}) text[s:e]={text[s:e]!r}")
