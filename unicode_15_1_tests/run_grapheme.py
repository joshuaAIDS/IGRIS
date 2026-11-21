from pathlib import Path
import unicodedataplus as u

TEST_FILE = Path(r"C:\IGRIS\unicode_15_1_tests\GraphemeBreakTest.txt")

assert u.unidata_version == "15.1.0"

def get_props(ch):
    return (
        u.grapheme_cluster_break(ch),
        u.indic_conjunct_break(ch),
        u.is_extended_pictographic(ch),
    )

def should_break(chars, i):
    a = chars[i - 1]
    b = chars[i]

    ga, ia, _ = get_props(a)
    gb, ib, epb = get_props(b)

    # GB3
    if ga == "CR" and gb == "LF":
        return False

    # GB4 / GB5
    if ga in ("Control", "CR", "LF"):
        return True
    if gb in ("Control", "CR", "LF"):
        return True

    # GB6
    if ga == "L" and gb in ("L", "V", "LV", "LVT"):
        return False

    # GB7
    if ga in ("LV", "V") and gb in ("V", "T"):
        return False

    # GB8
    if ga in ("LVT", "T") and gb == "T":
        return False

    # GB9
    if gb in ("Extend", "ZWJ"):
        return False

    # GB9a
    if gb == "SpacingMark":
        return False

    # GB9b
    if ga == "Prepend":
        return False

    # GB9c: Indic conjunct sequences
    if ib == "Consonant":
        j = i - 1
        saw_linker = False

        while j >= 0:
            incb = get_props(chars[j])[1]

            if incb == "Linker":
                saw_linker = True
                j -= 1
            elif incb == "Extend":
                j -= 1
            else:
                break

        if saw_linker and j >= 0:
            if get_props(chars[j])[1] == "Consonant":
                return False

    # GB11: Extended pictographic ZWJ sequences
    if epb and ga == "ZWJ":
        j = i - 2

        while j >= 0 and get_props(chars[j])[0] == "Extend":
            j -= 1

        if j >= 0 and get_props(chars[j])[2]:
            return False

    # GB12 / GB13: Regional Indicator pairs
    if ga == "Regional_Indicator" and gb == "Regional_Indicator":
        count = 0
        j = i - 1

        while j >= 0 and get_props(chars[j])[0] == "Regional_Indicator":
            count += 1
            j -= 1

        if count % 2 == 1:
            return False

    # GB999
    return True

def actual_boundaries(chars):
    boundaries = [0]

    for i in range(1, len(chars)):
        if should_break(chars, i):
            boundaries.append(i)

    boundaries.append(len(chars))
    return boundaries

total = 0
failures = []

with TEST_FILE.open("r", encoding="utf-8") as f:
    for line_no, line in enumerate(f, 1):
        line = line.split("#", 1)[0].strip()

        if not line:
            continue

        tokens = line.split()
        chars = []
        expected = []

        for token in tokens:
            if token in ("÷", "×"):
                if token == "÷":
                    expected.append(len(chars))
            else:
                chars.append(chr(int(token, 16)))

        actual = actual_boundaries(chars)
        total += 1

        if actual != expected:
            failures.append({
                "line": line_no,
                "expected": expected,
                "actual": actual,
                "codepoints": [f"U+{ord(c):04X}" for c in chars],
            })

print("Unicode version:", u.unidata_version)
print("Official test cases:", total)
print("Failures:", len(failures))

for failure in failures[:20]:
    print("FAIL:", failure)

print("RESULT:", "PASS" if not failures else "FAIL")
