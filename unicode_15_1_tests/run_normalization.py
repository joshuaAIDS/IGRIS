from pathlib import Path
import unicodedata2 as ud

test_file = Path(r"C:\IGRIS\unicode_15_1_tests\NormalizationTest.txt")

assert ud.unidata_version == "15.1.0", ud.unidata_version

total = 0
failures = []

with test_file.open("r", encoding="utf-8") as f:
    for line_no, line in enumerate(f, 1):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue

        columns = [x.strip() for x in line.split(";")]
        if len(columns) < 5:
            continue

        vectors = [
            "".join(chr(int(cp, 16)) for cp in col.split())
            for col in columns[:5]
        ]

        c1, c2, c3, c4, c5 = vectors

        checks = [
            ("NFC(c1)", ud.normalize("NFC", c1), c2),
            ("NFC(c2)", ud.normalize("NFC", c2), c2),
            ("NFC(c3)", ud.normalize("NFC", c3), c2),
            ("NFC(c4)", ud.normalize("NFC", c4), c4),
            ("NFC(c5)", ud.normalize("NFC", c5), c4),
            ("NFD(c1)", ud.normalize("NFD", c1), c3),
            ("NFD(c2)", ud.normalize("NFD", c2), c3),
            ("NFD(c3)", ud.normalize("NFD", c3), c3),
            ("NFD(c4)", ud.normalize("NFD", c4), c5),
            ("NFD(c5)", ud.normalize("NFD", c5), c5),
        ]

        for name, actual, expected in checks:
            total += 1
            if actual != expected:
                failures.append((line_no, name))

print("Unicode version:", ud.unidata_version)
print("Normalization assertions:", total)
print("Failures:", len(failures))

for failure in failures[:20]:
    print("FAIL:", failure)

print("RESULT:", "PASS" if not failures else "FAIL")
