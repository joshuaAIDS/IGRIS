"""TS-BAT shared batch-contract tests.

These tests exercise validation and a small contract probe only. They do not
claim that either production candidate exposes a working batch API.
"""

from .validation import require_text_batch, require_id_batch, require_text


def _contract_encode_batch(items, encode_one, calls):
    """Reference contract probe: validate the complete batch before backend use."""
    validated = require_text_batch(items)
    return [encode_one(item, calls) for item in validated]


def run_batch_contract_tests():
    results = []

    def record(test_id, name, fn):
        try:
            fn()
        except Exception as exc:
            results.append((test_id, name, "FAIL",
                            f"{type(exc).__name__}: {exc}"))
        else:
            results.append((test_id, name, "PASS", ""))

    def rejects(fn, expected):
        try:
            fn()
        except expected:
            return
        raise AssertionError(f"Expected {expected.__name__}")

    def probe(items):
        calls = []
        def encode_one(text, seen):
            seen.append(text)
            return f"encoded:{text}"
        output = _contract_encode_batch(items, encode_one, calls)
        return output, calls

    record("TS-BAT-01", "Accept empty text batch",
           lambda: (lambda r: (_ for _ in ()).throw(AssertionError(r))
                    if r != ([], []) else None)(probe([])))
    record("TS-BAT-02", "Single-item batch preserves item",
           lambda: (lambda r: (_ for _ in ()).throw(AssertionError(r))
                    if r != (["encoded:hello"], ["hello"]) else None)
                    (probe(["hello"])))
    record("TS-BAT-03", "Multiple-item batch preserves order",
           lambda: (lambda r: (_ for _ in ()).throw(AssertionError(r))
                    if r != (["encoded:first", "encoded:second", "encoded:third"],
                             ["first", "second", "third"]) else None)
                    (probe(["first", "second", "third"])))
    record("TS-BAT-04", "Empty strings retain their batch positions",
           lambda: (lambda r: (_ for _ in ()).throw(AssertionError(r))
                    if r != (["encoded:a", "encoded:", "encoded:b"],
                             ["a", "", "b"]) else None)
                    (probe(["a", "", "b"])))
    record("TS-BAT-05", "Reject string instead of batch sequence",
           lambda: rejects(lambda: require_text_batch("not-a-batch"), TypeError))
    record("TS-BAT-06", "Reject invalid first item",
           lambda: rejects(lambda: probe([None, "valid"]), TypeError))
    record("TS-BAT-07", "Reject invalid middle item",
           lambda: rejects(lambda: probe(["valid", None, "valid"]), TypeError))
    record("TS-BAT-08", "Reject invalid final item",
           lambda: rejects(lambda: probe(["valid", "valid", b"bytes"]), TypeError))
    record("TS-BAT-09", "Validate entire batch before backend calls",
           lambda: (lambda calls: (
               rejects(lambda: _contract_encode_batch(
                   ["valid", None], lambda item, seen: seen.append(item), calls
               ), TypeError),
               None if calls == [] else (_ for _ in ()).throw(
                   AssertionError(f"Backend called before validation: {calls}"))
           ))([]))
    record("TS-BAT-10", "Accept empty ID batch",
           lambda: require_id_batch([]))
    record("TS-BAT-11", "ID batch preserves row and token order",
           lambda: (lambda value: None if value == [[12, 13], [14], []]
                    else (_ for _ in ()).throw(AssertionError(value)))
                    (require_id_batch([[12, 13], [14], []])))
    record("TS-BAT-12", "Reject invalid token in later ID row",
           lambda: rejects(lambda: require_id_batch([[12], [13, True]]), TypeError))
    record("TS-BAT-13", "Reject structural ID in later ID row",
           lambda: rejects(lambda: require_id_batch([[12], [1]]), ValueError))
    record("TS-BAT-14", "Reject non-sequence ID batch",
           lambda: rejects(lambda: require_id_batch("12"), TypeError))
    record("TS-BAT-15", "Individual and batch input validation agree",
           lambda: (lambda values: None if all(
               require_text(value) == value for value in values
           ) and require_text_batch(values) == values else
               (_ for _ in ()).throw(AssertionError("Validation mismatch"))
           )(["", "English", "தமிழ்", "Tanglish"]))
    record("TS-BAT-16", "Invalid batch does not return partial output",
           lambda: rejects(lambda: probe(["ok", None, "later"]), TypeError))

    return results


if __name__ == "__main__":
    rows = run_batch_contract_tests()
    for test_id, name, status, detail in rows:
        print(f"{test_id:14} {status:4} {name}")
        if detail:
            print("   ", detail)
    passed = sum(row[2] == "PASS" for row in rows)
    failed = len(rows) - passed
    print(f"TOTAL: {len(rows)} | PASS: {passed} | FAIL: {failed}")
    raise SystemExit(1 if failed else 0)
