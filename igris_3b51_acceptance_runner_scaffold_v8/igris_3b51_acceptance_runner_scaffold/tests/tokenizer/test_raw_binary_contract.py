"""TS-BIN backend-independent raw-binary codec contract tests."""
from .raw_binary_codec import RawBinaryCodec


def _identity_mapping():
    # Synthetic mapping for contract tests only; not Candidate A/B vocab IDs.
    return list(range(12, 268))


def run_raw_binary_contract_tests():
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

    codec = RawBinaryCodec(_identity_mapping())

    record("TS-BIN-01", "Empty bytes encode to empty IDs",
           lambda: eq(codec.encode(b""), []))
    record("TS-BIN-02", "Empty ID sequence decodes to empty bytes",
           lambda: eq(codec.decode([]), b""))
    record("TS-BIN-03", "All 256 byte values round-trip exactly",
           lambda: eq(codec.decode(codec.encode(bytes(range(256))),
                                   ), bytes(range(256))))
    record("TS-BIN-04", "Arbitrary binary sequence round-trips",
           lambda: (lambda raw: eq(codec.decode(codec.encode(raw)), raw))
                   (b"\x00\xff\x80\xfeIGRIS\x00\x10"))
    record("TS-BIN-05", "Repeated bytes preserve exact order",
           lambda: eq(codec.decode(codec.encode(b"\x00\xff\x00\xff")), b"\x00\xff\x00\xff"))
    record("TS-BIN-06", "Single zero byte round-trips",
           lambda: eq(codec.decode(codec.encode(b"\x00")), b"\x00"))
    record("TS-BIN-07", "Single 0xFF byte round-trips",
           lambda: eq(codec.decode(codec.encode(b"\xff")), b"\xff"))
    record("TS-BIN-08", "Reject str input to binary encoder",
           lambda: rejects(lambda: codec.encode("not bytes"), TypeError))
    record("TS-BIN-09", "Reject bytearray input to binary encoder",
           lambda: rejects(lambda: codec.encode(bytearray(b"x")), TypeError))
    record("TS-BIN-10", "Reject memoryview input to binary encoder",
           lambda: rejects(lambda: codec.encode(memoryview(b"x")), TypeError))
    record("TS-BIN-11", "Reject non-sequence token IDs",
           lambda: rejects(lambda: codec.decode("12"), TypeError))
    record("TS-BIN-12", "Reject bool token ID",
           lambda: rejects(lambda: codec.decode([True]), TypeError))
    record("TS-BIN-13", "Reject structural token ID in binary decode",
           lambda: rejects(lambda: codec.decode([1]), ValueError))
    record("TS-BIN-14", "Reject valid content ID outside byte mapping",
           lambda: rejects(lambda: codec.decode([300]), ValueError))
    record("TS-BIN-15", "Reject negative token ID",
           lambda: rejects(lambda: codec.decode([-1]), ValueError))
    record("TS-BIN-16", "Reject token ID outside vocabulary",
           lambda: rejects(lambda: codec.decode([32768]), ValueError))
    record("TS-BIN-17", "Require exactly 256 mapping entries",
           lambda: rejects(lambda: RawBinaryCodec([12] * 255), ValueError))
    record("TS-BIN-18", "Reject duplicate byte-to-token mappings",
           lambda: rejects(lambda: RawBinaryCodec([12] * 256), ValueError))
    record("TS-BIN-19", "Reject structural IDs in mapping",
           lambda: rejects(lambda: RawBinaryCodec([0] + list(range(13, 268))), ValueError))
    record("TS-BIN-20", "Reject bool values in mapping",
           lambda: rejects(lambda: RawBinaryCodec([True] + list(range(13, 268))), TypeError))
    record("TS-BIN-21", "Reject non-sequence mapping",
           lambda: rejects(lambda: RawBinaryCodec("x"), TypeError))
    record("TS-BIN-22", "Text-like Unicode bytes remain byte-exact",
           lambda: (lambda raw: eq(codec.decode(codec.encode(raw)), raw))
                   ("தமிழ்".encode("utf-8")))
    record("TS-BIN-23", "Binary mode performs no Unicode normalization",
           lambda: (lambda raw: eq(codec.decode(codec.encode(raw)), raw))
                   (b"e\xcc\x81"))
    record("TS-BIN-24", "Decode rejects content IDs not in byte map",
           lambda: rejects(lambda: codec.decode([32767]), ValueError))

    return rows


if __name__ == "__main__":
    rows = run_raw_binary_contract_tests()
    for test_id, name, status, detail in rows:
        print(f"{test_id:14} {status:4} {name}")
        if detail:
            print("   ", detail)
    passed = sum(row[2] == "PASS" for row in rows)
    failed = len(rows) - passed
    print(f"TOTAL: {len(rows)} | PASS: {passed} | FAIL: {failed}")
    raise SystemExit(1 if failed else 0)
