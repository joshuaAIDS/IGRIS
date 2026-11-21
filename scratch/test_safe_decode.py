from tokenizers import Tokenizer

tok = Tokenizer.from_file('artifacts/tokenizer/candidate_a/tokenizer.json')

def bytes_char_mapping():
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return {chr(c): b for b, c in zip(bs, cs)}

byte_dec = bytes_char_mapping()

def decode_token_safely(token_str: str) -> tuple[str, bytes]:
    raw_bytes = bytes([byte_dec[c] for c in token_str])
    try:
        decoded = raw_bytes.decode('utf-8')
    except UnicodeDecodeError:
        decoded = ''.join(f'<0x{b:02X}>' for b in raw_bytes)
    return decoded, raw_bytes

for text in ['server-ல்', 'complex-ஆ', 'deploy பண்ணினோம்', 'memory allocation']:
    enc = tok.encode(text)
    pieces = []
    all_b = bytearray()
    for tid, tstr, (s, e) in zip(enc.ids, enc.tokens, enc.offsets):
        dec, raw_b = decode_token_safely(tstr)
        all_b.extend(raw_b)
        pieces.append((tid, tstr, dec, raw_b.hex(), s, e))
    reconstructed = all_b.decode('utf-8')
    print(f"\nText: {text} | Reconstructed: {reconstructed} | Match: {reconstructed == text}")
    for p in pieces:
        print(f"  id={p[0]:5d} | piece={p[1]!r:10s} | decoded={p[2]!r:12s} | hex={p[3]:8s} | span=[{p[4]}:{p[5]}]")
