import json
import hashlib
from tokenizers import Tokenizer

CANDIDATE_A_PATH = "artifacts/tokenizer/candidate_a/tokenizer.json"
CANDIDATE_B_PATH = "artifacts/tokenizer/candidate_b/tokenizer.model"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def byte_char_mapping():
    # ByteLevel BPE standard mapping
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return {chr(c): b for b, c in zip(bs, cs)}

CHAR_TO_BYTE = byte_char_mapping()

def raw_bpe_to_bytes(piece: str) -> bytes:
    return bytes([CHAR_TO_BYTE[c] for c in piece if c in CHAR_TO_BYTE])

def safe_decode_piece(raw_bytes: bytes) -> str:
    try:
        return raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return "".join(f"<0x{b:02X}>" for b in raw_bytes)

def run_narrow_audit():
    tokenizer = Tokenizer.from_file(CANDIDATE_A_PATH)
    
    expressions = [
        "server-ல்",
        "complex-ஆ",
        "deploy பண்ணினோம்",
        "memory allocation",
        "pannirukkom",
        "testing-க்கு"
    ]
    
    audit_results = []
    
    for text in expressions:
        enc = tokenizer.encode(text, add_special_tokens=False)
        token_ids = enc.ids
        raw_bpe_pieces = enc.tokens
        offsets = enc.offsets
        
        all_raw_bytes = bytearray()
        token_details = []
        
        for tid, raw_piece, (start_char, end_char) in zip(token_ids, raw_bpe_pieces, offsets):
            piece_bytes = raw_bpe_to_bytes(raw_piece)
            all_raw_bytes.extend(piece_bytes)
            decoded_display = safe_decode_piece(piece_bytes)
            
            token_details.append({
                "token_id": tid,
                "raw_bpe": raw_piece,
                "raw_hex": piece_bytes.hex(),
                "decoded_display": decoded_display,
                "char_offsets": [start_char, end_char],
                "char_slice": text[start_char:end_char]
            })
            
        reconstructed_text = all_raw_bytes.decode("utf-8", errors="replace")
        is_exact = (reconstructed_text == text) and (all_raw_bytes == text.encode("utf-8"))
        
        audit_results.append({
            "expression": text,
            "token_count": len(token_ids),
            "exact_bitwise_reconstruction": is_exact,
            "tokens": token_details
        })
        
    return audit_results

if __name__ == "__main__":
    results = run_narrow_audit()
    print(json.dumps(results, indent=2, ensure_ascii=False))
