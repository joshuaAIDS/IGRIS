"""TS-REN backend-independent trusted-sequence rendering tests."""
from .sequence_rendering import render_sequence, decode_content_ids
from .acceptance_config import STRUCTURAL_TOKENS


def run_rendering_contract_tests():
    rows = []

    def record(test_id, name, fn):
        try:
            fn()
        except Exception as exc:
            rows.append((test_id, name, "FAIL",
                         f"{type(exc).__name__}: {exc}"))
        else:
            rows.append((test_id, name, "PASS", ""))

    def eq(actual, expected):
        if actual != expected:
            raise AssertionError(f"{actual!r} != {expected!r}")

    def rejects(fn, expected):
        try:
            fn()
        except expected:
            return
        raise AssertionError(f"Expected {expected.__name__}")

    # Reference content decoder maps test IDs to visible markers.
    def decoder(ids):
        return "".join(chr(0x41 + (value - 12)) for value in ids)

    record("TS-REN-01", "Render every structural token by fixed ID",
           lambda: eq(render_sequence(list(range(12)), decoder),
                      "".join(STRUCTURAL_TOKENS)))
    record("TS-REN-02", "Decode a content-only sequence",
           lambda: eq(decode_content_ids([12, 13, 14], decoder), "ABC"))
    record("TS-REN-03", "Reject structural IDs in content-only decoding",
           lambda: rejects(lambda: decode_content_ids([12, 1], decoder), ValueError))
    record("TS-REN-04", "Render content before and after structural token",
           lambda: eq(render_sequence([12, 9, 13], decoder), "A<|system|>B"))
    record("TS-REN-05", "Render mixed multiple content spans in order",
           lambda: eq(render_sequence([12, 13, 11, 14, 15, 2, 16], decoder),
                      "AB<|assistant|>CD<|end_of_text|>E"))
    record("TS-REN-06", "Render consecutive structural tokens",
           lambda: eq(render_sequence([9, 10, 11], decoder),
                      "<|system|><|user|><|assistant|>"))
    record("TS-REN-07", "Render content between consecutive structures",
           lambda: eq(render_sequence([9, 12, 10, 11, 13], decoder),
                      "<|system|>A<|user|><|assistant|>B"))
    record("TS-REN-08", "Empty trusted sequence renders empty string",
           lambda: eq(render_sequence([], decoder), ""))
    record("TS-REN-09", "Single content token renders",
           lambda: eq(render_sequence([12], decoder), "A"))
    record("TS-REN-10", "Single structural token renders",
           lambda: eq(render_sequence([0], decoder), "<|pad|>"))
    record("TS-REN-11", "Do not trim decoded content",
           lambda: eq(render_sequence([12, 13], lambda ids: "  x \n"), "  x \n"))
    record("TS-REN-12", "Do not normalize decoded content",
           lambda: eq(render_sequence([12], lambda ids: "e\u0301"), "e\u0301"))
    record("TS-REN-13", "Decode maximal contiguous content spans together",
           lambda: (lambda calls: (
               eq(render_sequence([12, 13, 9, 14, 15], 
                   lambda ids: (calls.append(list(ids)) or decoder(ids))), "AB<|system|>CD"),
               eq(calls, [[12, 13], [14, 15]])
           ))([]))
    record("TS-REN-14", "Reject negative trusted token ID",
           lambda: rejects(lambda: render_sequence([-1], decoder), ValueError))
    record("TS-REN-15", "Reject token ID outside vocabulary",
           lambda: rejects(lambda: render_sequence([32768], decoder), ValueError))
    record("TS-REN-16", "Reject bool token ID",
           lambda: rejects(lambda: render_sequence([True], decoder), TypeError))
    record("TS-REN-17", "Reject non-sequence input",
           lambda: rejects(lambda: render_sequence("12", decoder), TypeError))
    record("TS-REN-18", "Reject decoder callback returning non-string",
           lambda: rejects(lambda: render_sequence([12], lambda ids: 123), TypeError))
    record("TS-REN-19", "Validate all IDs before invoking decoder",
           lambda: (lambda calls: (
               rejects(lambda: render_sequence([12, 32768], 
                   lambda ids: (calls.append(ids) or decoder(ids))), ValueError),
               eq(calls, [])
           ))([]))
    record("TS-REN-20", "Structural token in middle does not merge content spans",
           lambda: (lambda calls: (
               eq(render_sequence([12, 1, 13], 
                   lambda ids: (calls.append(list(ids)) or decoder(ids))),
                   "A<|begin_of_text|>B"),
               eq(calls, [[12], [13]])
           ))([]))

    return rows


if __name__ == "__main__":
    rows = run_rendering_contract_tests()
    for test_id, name, status, detail in rows:
        print(f"{test_id:14} {status:4} {name}")
        if detail:
            print("   ", detail)
    passed = sum(row[2] == "PASS" for row in rows)
    failed = len(rows) - passed
    print(f"TOTAL: {len(rows)} | PASS: {passed} | FAIL: {failed}")
    raise SystemExit(1 if failed else 0)
