import urllib.request
import json

cases = ['server-ல்', 'complex-ஆ', 'deploy பண்ணினோம்', 'memory allocation', 'pannirukkom', 'testing-க்கு']

print("=================================================================")
print("LIVE BACKEND TOKENIZER EXACTNESS & ROUND-TRIP AUDIT")
print("=================================================================")

for c in cases:
    payload = json.dumps({'text': c}).encode('utf-8')
    req = urllib.request.Request(
        'http://127.0.0.1:8000/v1/tokenize',
        data=payload,
        headers={'Content-Type': 'application/json'}
    )
    res = urllib.request.urlopen(req)
    data = json.loads(res.read().decode('utf-8'))
    tids = [t['id'] for t in data['tokens']]
    pieces = [t['piece'] for t in data['tokens']]
    decoded_pieces = [t['decoded'] for t in data['tokens']]
    hex_pieces = [t.get('raw_hex') for t in data['tokens']]

    print(f"\nExpression: '{c}'")
    print(f"  Token Count (Actual): {data['token_count']}")
    print(f"  Token IDs: {tids}")
    print(f"  Raw BPE Pieces: {pieces}")
    print(f"  Decoded Unicode / Safe Hex: {decoded_pieces}")
    print(f"  Raw Hex: {hex_pieces}")
    print(f"  Exact Bitwise Round-Trip: {data['exact_roundtrip']}")
    print(f"  Reconstructed Text: '{data['reconstructed_text']}'")
    assert data['exact_roundtrip'] is True, f"Mismatch on {c}!"
    assert data['reconstructed_text'] == c, f"Content mismatch on {c}!"

print("\nALL 6 MANDATORY EXPRESSIONS PASSED 100% BITWISE ROUND-TRIP EXACTNESS!")
