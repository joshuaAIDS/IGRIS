"""Backend-independent Unicode and structural-spelling escaping helpers."""
from __future__ import annotations
from .acceptance_config import STRUCTURAL_TOKENS

SENTINEL = "\U000F0000"
WORDSPACE = "\u2581"

def _unicode_module():
    try:
        import unicodedata2 as ud
    except ImportError as exc:
        raise RuntimeError("Unicode 15.1 engine unavailable; no installation is attempted") from exc
    if getattr(ud, "unidata_version", None) != "15.1.0":
        raise RuntimeError(f"Unicode engine must be 15.1.0, got {getattr(ud, 'unidata_version', 'unknown')}")
    return ud

def normalize_nfc(text: str) -> str:
    from .validation import require_text
    return _unicode_module().normalize("NFC", require_text(text))

def escape_text(text: str, *, mode: str = "text_mode") -> str:
    from .validation import require_text
    require_text(text)
    if mode not in ("text_mode", "exact_unicode_mode"):
        raise ValueError("mode must be text_mode or exact_unicode_mode")
    if mode == "text_mode":
        text = normalize_nfc(text)
    tokens = sorted(STRUCTURAL_TOKENS, key=len, reverse=True)
    by_token = {token: f"{SENTINEL}S{i:02d};" for i, token in enumerate(STRUCTURAL_TOKENS)}
    out, i = [], 0
    while i < len(text):
        if text.startswith(SENTINEL, i):
            out.append(SENTINEL + SENTINEL); i += len(SENTINEL); continue
        if text.startswith(WORDSPACE, i):
            out.append(SENTINEL + "W;"); i += len(WORDSPACE); continue
        match = next((token for token in tokens if text.startswith(token, i)), None)
        if match is not None:
            out.append(by_token[match]); i += len(match); continue
        out.append(text[i]); i += 1
    return "".join(out)

def unescape_text(text: str) -> str:
    from .validation import require_text
    require_text(text)
    by_code = {f"S{i:02d};": token for i, token in enumerate(STRUCTURAL_TOKENS)}
    out, i = [], 0
    while i < len(text):
        if not text.startswith(SENTINEL, i):
            out.append(text[i]); i += 1; continue
        start = i
        i += len(SENTINEL)
        if text.startswith(SENTINEL, i):
            out.append(SENTINEL); i += len(SENTINEL); continue
        if text.startswith("W;", i):
            out.append(WORDSPACE); i += 2; continue
        code = text[i:i+4]
        if code in by_code:
            out.append(by_code[code]); i += 4; continue
        raise ValueError(f"malformed, unknown, or noncanonical escape at index {start}")
    return "".join(out)
