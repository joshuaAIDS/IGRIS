from tokenizers import Tokenizer
from tokenizers.decoders import ByteLevel

tok = Tokenizer.from_file('artifacts/tokenizer/candidate_a/tokenizer.json')

text = 'deploy பண்ணினோம்'
enc = tok.encode(text)

# Using tok.id_to_token
# HuggingFace tokenizers ByteLevel decoder
# Let's see how token pieces map to raw bytes:
import tokenizers.pre_tokenizers

# The standard byte-level map from HuggingFace
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

# For each token, get its raw bytes
token_bytes_list = []
for token_str in enc.tokens:
    # convert BPE chars back to raw bytes
    token_bytes = bytes([byte_dec[c] for c in token_str])
    token_bytes_list.append(token_bytes)

# Concatenating all token bytes reproduces the UTF-8 bytes of text!
all_bytes = b''.join(token_bytes_list)
print("All bytes match text.encode('utf-8'):", all_bytes == text.encode('utf-8'))
print("Decoded all bytes:", all_bytes.decode('utf-8'))
