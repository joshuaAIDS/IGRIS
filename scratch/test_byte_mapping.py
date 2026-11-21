from tokenizers import pre_tokenizers

# Standard GPT-2 byte mapping used by ByteLevel BPE
def bytes_to_unicode():
    bs = (
        list(range(ord("!"), ord("~") + 1))
        + list(range(ord("¡"), ord("¬") + 1))
        + list(range(ord("®"), ord("ÿ") + 1))
    )
    cs = bs[:]
    n = 0
    for b in range(2**8):
        if b not in bs:
            bs.append(b)
            cs.append(2**8 + n)
            n += 1
    cs = [chr(n) for n in cs]
    return dict(zip(bs, cs))

byte_to_char_map = bytes_to_unicode()
char_to_byte_map = {v: k for k, v in byte_to_char_map.items()}

def raw_token_to_bytes(tok_str: str) -> bytes:
    b_arr = bytearray()
    for ch in tok_str:
        if ch in char_to_byte_map:
            b_arr.append(char_to_byte_map[ch])
        else:
            b_arr.extend(ch.encode("utf-8"))
    return bytes(b_arr)

def decode_token_bytes(tok_str: str) -> str:
    raw_b = raw_token_to_bytes(tok_str)
    try:
        return raw_b.decode("utf-8")
    except UnicodeDecodeError:
        # Incomplete UTF-8 sequence, show hex byte representation e.g. <0xE0><0xAE>
        return "".join(f"<0x{b:02X}>" for b in raw_b)

for sample in ["à®²", "à¯į", "à®", "Ĩ", "Ġà®ªà®£", "ser", "ver", "Ġ"]:
    b = raw_token_to_bytes(sample)
    dec = decode_token_bytes(sample)
    print(f"raw {sample!r:12} -> bytes {b.hex(' '):12} -> decoded: {dec!r}")
