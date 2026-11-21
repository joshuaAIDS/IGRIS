"""TS-UNI and TS-SEC backend-independent Unicode/escaping checks."""
from .unicode_security import (
    SENTINEL, WORDSPACE, escape_text, unescape_text, normalize_nfc,
)
from .acceptance_config import STRUCTURAL_TOKENS

def run_unicode_security_tests():
    rows = []
    def record(test_id, name, fn):
        try:
            fn()
        except RuntimeError as exc:
            rows.append((test_id, name, "BLOCKED", str(exc)))
        except Exception as exc:
            rows.append((test_id, name, "FAIL", f"{type(exc).__name__}: {exc}"))
        else:
            rows.append((test_id, name, "PASS", ""))

    def eq(actual, expected):
        if actual != expected:
            raise AssertionError(f"{actual!r} != {expected!r}")
    def rejects(fn):
        try: fn()
        except ValueError: return
        raise AssertionError("Expected ValueError")

    # Unicode normalization contract (Unicode 15.1 engine required).
    record("TS-UNI-01", "NFC composes decomposed Latin", lambda: eq(normalize_nfc("e\u0301"), "é"))
    record("TS-UNI-02", "NFC composes decomposed Tamil sequence where defined",
           lambda: eq(normalize_nfc("கி"), "கி"))
    record("TS-UNI-03", "Exact mode preserves decomposed codepoints",
           lambda: eq(escape_text("e\u0301", mode="exact_unicode_mode"), "e\u0301"))
    record("TS-UNI-04", "Text mode normalizes before escaping",
           lambda: eq(unescape_text(escape_text("e\u0301")), "é"))
    record("TS-UNI-05", "Reject unknown mode",
           lambda: rejects(lambda: escape_text("x", mode="raw_binary_mode")))

    # Sentinel, SentencePiece whitespace marker, and every structural spelling.
    record("TS-SEC-01", "Literal sentinel is doubled",
           lambda: eq(escape_text(SENTINEL, mode="exact_unicode_mode"), SENTINEL * 2))
    record("TS-SEC-02", "Literal U+2581 uses W escape",
           lambda: eq(escape_text(WORDSPACE, mode="exact_unicode_mode"), SENTINEL + "W;"))
    record("TS-SEC-03", "All 12 structural spellings use fixed S00-S11 escapes",
           lambda: eq(escape_text("".join(STRUCTURAL_TOKENS), mode="exact_unicode_mode"),
                      "".join(f"{SENTINEL}S{i:02d};" for i in range(12))))
    record("TS-SEC-04", "Structural spellings round-trip as literal text",
           lambda: eq(unescape_text(escape_text(" ".join(STRUCTURAL_TOKENS), mode="exact_unicode_mode")),
                      " ".join(STRUCTURAL_TOKENS)))
    record("TS-SEC-05", "Mixed sentinel, marker, and structural text round-trip",
           lambda: eq(unescape_text(escape_text("A"+SENTINEL+WORDSPACE+"<|user|>தமிழ்",
                                                 mode="exact_unicode_mode")),
                      "A"+SENTINEL+WORDSPACE+"<|user|>தமிழ்"))
    record("TS-SEC-06", "Escape output contains no raw structural spelling",
           lambda: [(_ for _ in ()).throw(AssertionError(token))
                    for token in STRUCTURAL_TOKENS
                    if token in escape_text(token, mode="exact_unicode_mode")])
    record("TS-SEC-07", "Adjacent literal sentinels round-trip",
           lambda: eq(unescape_text(escape_text(SENTINEL*3, mode="exact_unicode_mode")), SENTINEL*3))
    record("TS-SEC-08", "Empty string round-trip",
           lambda: eq(unescape_text(escape_text("", mode="exact_unicode_mode")), ""))

    malformed = [
        SENTINEL, SENTINEL+"X;", SENTINEL+"S12;", SENTINEL+"S99;",
        SENTINEL+"S0;", SENTINEL+"S000;", SENTINEL+"W",
        SENTINEL+"s00;", SENTINEL+"S00", SENTINEL+"S00x",
    ]
    for index, value in enumerate(malformed, 9):
        record(f"TS-SEC-{index:02d}", f"Reject malformed/noncanonical escape {index-8}",
               lambda value=value: rejects(lambda: unescape_text(value)))

    # Ordinary multilingual strings and grapheme sequences preserve exactly in exact mode.
    samples = ["தமிழ்", "vanakkam machi", "தமிழ் + Tanglish", "👩🏽‍💻",
               "கொ", "நி", "🇮🇳", "क्ष"]
    for index, sample in enumerate(samples, 19):
        record(f"TS-UNI-{index:02d}", f"Exact Unicode round-trip sample {index-18}",
               lambda sample=sample: eq(unescape_text(escape_text(sample, mode="exact_unicode_mode")), sample))

    return rows
