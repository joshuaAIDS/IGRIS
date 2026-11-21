import json
from tokenizers import Tokenizer

tok = Tokenizer.from_file('artifacts/tokenizer/candidate_a/tokenizer.json')

test_cases = [
    ('English', 'The IGRIS architecture incorporates SwiGLU activations and RoPE embeddings.'),
    ('Tamil', 'இக்ரிஸ் மாதிரி தமிழ் மொழியை மிகச் சிறந்த முறையில் பகுப்பாய்வு செய்கிறது.'),
    ('Tanglish', 'deploy பண்ணினோம்'),
    ('Tanglish', 'server-ல்'),
    ('Tanglish', 'complex-ஆ'),
    ('English', 'memory allocation'),
    ('Tanglish', 'pannirukkom'),
    ('Tanglish', 'testing-க்கு'),
    ('Tamil', 'வணக்கம் உலகம்'),
]

all_passed = True
for lang, text in test_cases:
    enc = tok.encode(text)
    decoded_full = tok.decode(enc.ids)
    pieces_decoded = [tok.decode([tid]) for tid in enc.ids]
    reconstructed_concat = ''.join(pieces_decoded)
    sliced_pieces = [text[start:end] for start, end in enc.offsets]
    reconstructed_slices = ''.join(sliced_pieces)

    match_full = (text == decoded_full)
    match_concat = (text == reconstructed_concat)
    match_slices = (text == reconstructed_slices)

    print(f"=== [{lang}] '{text}' ===")
    print(f"  Tokens: {len(enc.ids)} | IDs: {enc.ids}")
    print(f"  Exact full decode: {match_full}")
    print(f"  Exact concat decode: {match_concat}")
    print(f"  Offsets span exact: {match_slices}")

    if not (match_full and match_concat and match_slices):
        all_passed = False
        print(f"  MISMATCH DETECTED: expected {repr(text)}, concat: {repr(reconstructed_concat)}, slices: {repr(reconstructed_slices)}")

print("\nOVERALL TOKENIZER EXACTNESS RESULT:", "PASSED" if all_passed else "FAILED")
