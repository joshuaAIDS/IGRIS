"""TS-VAL: backend-independent strict validation tests."""

from .validation import (
    require_text, require_bytes, require_token_id, require_id_sequence,
    require_text_batch, require_id_batch,
)

def run_validation_tests():
    results = []

    def record(test_id, name, fn):
        try:
            fn()
        except Exception as exc:
            results.append((test_id, name, "FAIL", f"{type(exc).__name__}: {exc}"))
        else:
            results.append((test_id, name, "PASS", ""))

    def accepts(fn):
        fn()

    def rejects(fn, expected):
        try:
            fn()
        except expected:
            return
        raise AssertionError(f"Expected {expected.__name__}")

    # Text and bytes are intentionally separate API domains.
    record("TS-VAL-01", "Accept ordinary text",
           lambda: accepts(lambda: require_text("Hello தமிழ் Tanglish")))
    record("TS-VAL-02", "Accept empty text",
           lambda: accepts(lambda: require_text("")))
    record("TS-VAL-03", "Reject None as text",
           lambda: rejects(lambda: require_text(None), TypeError))
    record("TS-VAL-04", "Reject bytes through text API",
           lambda: rejects(lambda: require_text(b"abc"), TypeError))
    record("TS-VAL-05", "Reject integer through text API",
           lambda: rejects(lambda: require_text(123), TypeError))
    record("TS-VAL-06", "Reject lone surrogate",
           lambda: rejects(lambda: require_text("x\ud800y"), ValueError))
    record("TS-VAL-07", "Accept bytes through binary API",
           lambda: accepts(lambda: require_bytes(b"\x00\xff")))
    record("TS-VAL-08", "Reject str through binary API",
           lambda: rejects(lambda: require_bytes("abc"), TypeError))

    # Strict token-ID typing and range.
    record("TS-VAL-09", "Accept first content ID",
           lambda: accepts(lambda: require_token_id(12)))
    record("TS-VAL-10", "Accept last vocabulary ID",
           lambda: accepts(lambda: require_token_id(32767)))
    record("TS-VAL-11", "Reject bool token ID",
           lambda: rejects(lambda: require_token_id(True), TypeError))
    record("TS-VAL-12", "Reject float token ID",
           lambda: rejects(lambda: require_token_id(12.0), TypeError))
    record("TS-VAL-13", "Reject string token ID",
           lambda: rejects(lambda: require_token_id("12"), TypeError))
    record("TS-VAL-14", "Reject None token ID",
           lambda: rejects(lambda: require_token_id(None), TypeError))
    record("TS-VAL-15", "Reject negative token ID",
           lambda: rejects(lambda: require_token_id(-1), ValueError))
    record("TS-VAL-16", "Reject ID equal to vocab size",
           lambda: rejects(lambda: require_token_id(32768), ValueError))

    # Structural IDs are reserved for trusted sequence rendering.
    record("TS-VAL-17", "Reject PAD ID in content",
           lambda: rejects(lambda: require_token_id(0), ValueError))
    record("TS-VAL-18", "Reject all structural IDs in content",
           lambda: [rejects(lambda i=i: require_token_id(i), ValueError)
                    for i in range(12)])
    record("TS-VAL-19", "Allow structural ID in trusted sequence",
           lambda: accepts(lambda: require_token_id(0, content_only=False)))
    record("TS-VAL-20", "Validate content ID sequence",
           lambda: accepts(lambda: require_id_sequence([12, 13, 32767])))

    # Batch validation, including atomic validation before backend calls.
    record("TS-VAL-21", "Accept empty text batch",
           lambda: accepts(lambda: require_text_batch([])))
    record("TS-VAL-22", "Accept empty strings in batch",
           lambda: accepts(lambda: require_text_batch(["", "தமிழ்"])))
    record("TS-VAL-23", "Reject non-sequence text batch",
           lambda: rejects(lambda: require_text_batch("abc"), TypeError))
    record("TS-VAL-24", "Reject invalid item in text batch",
           lambda: rejects(lambda: require_text_batch(["ok", None]), TypeError))
    record("TS-VAL-25", "Accept empty ID batch",
           lambda: accepts(lambda: require_id_batch([])))
    record("TS-VAL-26", "Reject invalid ID in later batch row",
           lambda: rejects(lambda: require_id_batch([[12], [True]]), TypeError))
    record("TS-VAL-27", "Reject structural ID in batch content",
           lambda: rejects(lambda: require_id_batch([[12], [1]]), ValueError))
    record("TS-VAL-28", "Reject bytes as ID sequence",
           lambda: rejects(lambda: require_id_sequence(b"\x0c"), TypeError))

    return results


if __name__ == "__main__":
    results = run_validation_tests()
    for test_id, name, status, detail in results:
        print(f"{test_id:14} {status:4} {name}")
        if detail:
            print("   ", detail)
    passed = sum(row[2] == "PASS" for row in results)
    failed = len(results) - passed
    print(f"TOTAL: {len(results)} | PASS: {passed} | FAIL: {failed}")
    raise SystemExit(1 if failed else 0)
