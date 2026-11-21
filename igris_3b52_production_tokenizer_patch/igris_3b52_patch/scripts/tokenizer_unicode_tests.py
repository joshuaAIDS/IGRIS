"""IGRIS Phase 15 — Tokenizer Indic Script Integrity and Robustness Test Suite.

Provides exhaustive test vectors verifying:
  1. Indic Dependent Vowels and Matras (all 7 Indic scripts)
  2. Viramas / Halants / Pulli
  3. Conjuncts, Wattulu, Ottu, and Yuktakshar
  4. Zero-Width Joiner (ZWJ, U+200D) and Zero-Width Non-Joiner (ZWNJ, U+200C)
  5. Unicode NFC Consistency
  6. Exact Lossless Round-Trip Preservation
  7. Robustness (empty strings, whitespace-heavy, emoji, long text, repetitions)
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from typing import Any, Sequence

from igris.tokenizer.strict import StrictTokenizer


@dataclass
class UnicodeTestCase:
    test_id: str
    category: str
    script: str
    description: str
    text: str
    expected_exact: bool = True


@dataclass
class TestCaseResult:
    test_id: str
    category: str
    script: str
    passed: bool
    exact_match: bool
    nfc_match: bool
    token_count: int
    char_count: int
    notes: str


@dataclass
class UnicodeIntegrityReport:
    total_tests: int
    passed_tests: int
    failed_tests: int
    exact_match_pct: float
    nfc_match_pct: float
    results: list[TestCaseResult] = field(default_factory=list)


INDIC_UNICODE_VECTORS: list[UnicodeTestCase] = [
    # -------------------------------------------------------------------------
    # 1. TAMIL SCRIPT INTEGRITY
    # -------------------------------------------------------------------------
    UnicodeTestCase(
        test_id="ta_vowel_01",
        category="Dependent Vowels & Matras",
        script="Tamil",
        description="Tamil base consonants combined with all 11 dependent vowel signs",
        text="கா கி கீ கு கூ கெ கே கை கொ கோ கௌ",
    ),
    UnicodeTestCase(
        test_id="ta_pulli_02",
        category="Viramas & Pulli",
        script="Tamil",
        description="Tamil consonants with pulli (virama U+0B8D) forming pure consonants",
        text="க் ங் ச் ஞ் ட் ண் த் ந் ப் ம் ய் ர் ல் வ் ழ் ள் ற் ன்",
    ),
    UnicodeTestCase(
        test_id="ta_grantha_03",
        category="Conjuncts & Grantha",
        script="Tamil",
        description="Tamil Grantha consonants and Sanskrit loan ligatures",
        text="ஸ்ரீ லக்ஷ்மி நரசிம்மர் ஸ்தலம் க்ஷேத்திரம்",
    ),
    UnicodeTestCase(
        test_id="ta_aytham_04",
        category="Special Characters",
        script="Tamil",
        description="Tamil Aytham character U+0B83 in context",
        text="எஃகு அஃது இஃது எஃகினம்",
    ),

    # -------------------------------------------------------------------------
    # 2. HINDI / DEVANAGARI INTEGRITY
    # -------------------------------------------------------------------------
    UnicodeTestCase(
        test_id="hi_matra_01",
        category="Dependent Vowels & Matras",
        script="Hindi/Devanagari",
        description="Devanagari consonants with all standard matras",
        text="का कि की कु कू कृ के कै को कौ कं कः",
    ),
    UnicodeTestCase(
        test_id="hi_halant_02",
        category="Viramas & Pulli",
        script="Hindi/Devanagari",
        description="Devanagari halant (U+094D) producing half-forms and conjuncts",
        text="क् ख् ग् घ् च् छ् ज् झ् ट् ठ् ड् ढ् त् थ् द् ध् न् प् फ् ब् भ् म्",
    ),
    UnicodeTestCase(
        test_id="hi_conjunct_03",
        category="Conjuncts & Grantha",
        script="Hindi/Devanagari",
        description="Complex Devanagari conjuncts (ksha, tra, jnya, shra)",
        text="क्षत्रिय त्रिशूल ज्ञान विज्ञान आश्रम राष्ट्र",
    ),
    UnicodeTestCase(
        test_id="hi_nukta_04",
        category="Nukta & Candrabindu",
        script="Hindi/Devanagari",
        description="Devanagari nukta characters and candrabindu nasals",
        text="फ़िल्म क़िला ज़मीन आँख चाँद ऊँट",
    ),

    # -------------------------------------------------------------------------
    # 3. TELUGU SCRIPT INTEGRITY
    # -------------------------------------------------------------------------
    UnicodeTestCase(
        test_id="te_vowel_01",
        category="Dependent Vowels & Matras",
        script="Telugu",
        description="Telugu consonants with dependent vowel signs",
        text="కా కి కీ కు కూ కృ కౄ కె కే కై కొ కో కౌ కం కః",
    ),
    UnicodeTestCase(
        test_id="te_virama_02",
        category="Viramas & Pulli",
        script="Telugu",
        description="Telugu virama (U+0C4D) and subscript consonants (wattulu)",
        text="క్ ఖ్ గ్ ఘ్ చ్ ఛ్ జ్ ఝ్ ట్ ఠ్ డ్ ఢ్ త్ థ్ ద్ ధ్ న్ ప్ ఫ్ బ్ భ్ మ్",
    ),
    UnicodeTestCase(
        test_id="te_wattulu_03",
        category="Conjuncts & Grantha",
        script="Telugu",
        description="Telugu complex conjuncts with subscript consonants",
        text="రక్తము భక్తి విద్యా శక్తి రాష్ట్రము",
    ),

    # -------------------------------------------------------------------------
    # 4. MALAYALAM SCRIPT & ZWJ / CHILLU INTEGRITY
    # -------------------------------------------------------------------------
    UnicodeTestCase(
        test_id="ml_vowel_01",
        category="Dependent Vowels & Matras",
        script="Malayalam",
        description="Malayalam consonants with vowel signs",
        text="കാ കി കീ കു കൂ കൃ കെ കേ കൈ കൊ കോ കൗ കം കഃ",
    ),
    UnicodeTestCase(
        test_id="ml_chillu_atomic_02",
        category="Chillu & ZWJ",
        script="Malayalam",
        description="Atomic Malayalam chillu characters (U+0D7A to U+0D7F)",
        text="ൺ ൻ ർ ൽ ൾ ൿ",
    ),
    UnicodeTestCase(
        test_id="ml_chillu_context_03",
        category="Chillu & ZWJ",
        script="Malayalam",
        description="Malayalam chillu letters in common words with chandrakkala",
        text="അവൻ അവൻ്റെ അവർ അവരുടെ പാൽ കാൽ കൺകൾ",
    ),
    UnicodeTestCase(
        test_id="ml_zwj_legacy_04",
        category="Chillu & ZWJ",
        script="Malayalam",
        description="Malayalam legacy chillu sequence using virama + ZWJ (U+200D)",
        text="അവന്‍\u200D അവള്‍\u200D അവര്‍\u200D",
    ),

    # -------------------------------------------------------------------------
    # 5. KANNADA SCRIPT INTEGRITY
    # -------------------------------------------------------------------------
    UnicodeTestCase(
        test_id="kn_vowel_01",
        category="Dependent Vowels & Matras",
        script="Kannada",
        description="Kannada consonants with vowel signs",
        text="ಕಾ ಕಿ ಕೀ ಕು ಕೂ ಕೃ ಕೆ ಕೇ ಕೈ ಕೊ ಕೋ ಕೌ ಕಂ ಕಃ",
    ),
    UnicodeTestCase(
        test_id="kn_ottu_02",
        category="Conjuncts & Grantha",
        script="Kannada",
        description="Kannada conjuncts with consonant subscripts (ottu forms)",
        text="ಕರ್ನಾಟಕ ಶಕ್ತಿ ಭಕ್ತಿ ರಾಷ್ಟ್ರ ವಿದ್ಯಾರ್ಥಿ",
    ),

    # -------------------------------------------------------------------------
    # 6. BENGALI SCRIPT INTEGRITY
    # -------------------------------------------------------------------------
    UnicodeTestCase(
        test_id="bn_vowel_01",
        category="Dependent Vowels & Matras",
        script="Bengali",
        description="Bengali consonants with vowel signs",
        text="কা কি কী কু কূ কৃ কে কৈ কো কৌ কং কঃ",
    ),
    UnicodeTestCase(
        test_id="bn_yuktakshar_02",
        category="Conjuncts & Grantha",
        script="Bengali",
        description="Bengali yuktakshar conjunct sequences with hasant",
        text="কলকাতা রবীন্দ্রনাথ বিজ্ঞান স্বাস্থ্য সৃষ্টি রাষ্ট্র",
    ),

    # -------------------------------------------------------------------------
    # 7. GUJARATI SCRIPT INTEGRITY
    # -------------------------------------------------------------------------
    UnicodeTestCase(
        test_id="gu_vowel_01",
        category="Dependent Vowels & Matras",
        script="Gujarati",
        description="Gujarati consonants with dependent vowel signs",
        text="કા કિ કી કુ કૂ કૃ કે કૈ કો કૌ કં કઃ",
    ),
    UnicodeTestCase(
        test_id="gu_conjunct_02",
        category="Conjuncts & Grantha",
        script="Gujarati",
        description="Gujarati conjuncts and viramas",
        text="ગુજરાત નમસ્તે વિદ્યા શક્તિ રાષ્ટ્ર",
    ),

    # -------------------------------------------------------------------------
    # 8. ZERO-WIDTH CHARACTERS & NFC CONSISTENCY
    # -------------------------------------------------------------------------
    UnicodeTestCase(
        test_id="zw_indic_zwnj_01",
        category="Zero-Width Handling",
        script="Indic",
        description="Indic conjunct prevention using ZWNJ (U+200C)",
        text="क्\u200Cष क्\u200Dत ক\u200Dত",
    ),
    UnicodeTestCase(
        test_id="nfc_decomposed_02",
        category="NFC Consistency",
        script="Multilingual",
        description="Canonical decomposed NFD text normalized through tokenizer",
        text=unicodedata.normalize("NFD", "Café naïve résumé தமிழ்நாடு हिंदी বাংলা"),
        expected_exact=False,
    ),

    # -------------------------------------------------------------------------
    # 9. ROBUSTNESS EDGE CASES
    # -------------------------------------------------------------------------
    UnicodeTestCase(
        test_id="robust_empty_01",
        category="Robustness",
        script="Universal",
        description="Empty string round-trip test",
        text="",
    ),
    UnicodeTestCase(
        test_id="robust_whitespace_02",
        category="Robustness",
        script="Universal",
        description="Whitespace variations: tabs, newlines, multiple spaces",
        text="   \t\t\n\n   leading,  middle   and  trailing  \t\n  ",
    ),
    UnicodeTestCase(
        test_id="robust_repeated_03",
        category="Robustness",
        script="Universal",
        description="Extremely repeated characters and punctuation",
        text="zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",
    ),
    UnicodeTestCase(
        test_id="robust_emoji_04",
        category="Robustness",
        script="Universal",
        description="High-density emoji and compound Unicode symbols",
        text="🔥 💯 🚀 🇮🇳 👩‍💻 👨‍👩‍👧‍👦 🤖",
    ),
    UnicodeTestCase(
        test_id="robust_long_05",
        category="Robustness",
        script="Universal",
        description="Long text sequence exceeding 1000 characters",
        text=("IGRIS multilingual decoder tokenizer robustness evaluation test sequence. " * 20),
    ),
]


def run_unicode_integrity_suite(tokenizer: StrictTokenizer) -> UnicodeIntegrityReport:
    """Execute all Unicode integrity and robustness test vectors on a tokenizer."""
    results: list[TestCaseResult] = []

    for vec in INDIC_UNICODE_VECTORS:
        token_ids = tokenizer.encode_content(vec.text)
        decoded = tokenizer.decode_content(token_ids)

        exact_match = (decoded == vec.text)
        nfc_match = (unicodedata.normalize("NFC", decoded) == unicodedata.normalize("NFC", vec.text))

        passed = exact_match if vec.expected_exact else nfc_match
        notes = "Fidelity 100%" if passed else f"Mismatch: expected len={len(vec.text)}, decoded len={len(decoded)}"

        results.append(
            TestCaseResult(
                test_id=vec.test_id,
                category=vec.category,
                script=vec.script,
                passed=passed,
                exact_match=exact_match,
                nfc_match=nfc_match,
                token_count=len(token_ids),
                char_count=len(vec.text),
                notes=notes,
            )
        )

    total = len(results)
    passed_count = sum(1 for r in results if r.passed)
    exact_count = sum(1 for r in results if r.exact_match)
    nfc_count = sum(1 for r in results if r.nfc_match)

    return UnicodeIntegrityReport(
        total_tests=total,
        passed_tests=passed_count,
        failed_tests=total - passed_count,
        exact_match_pct=round((exact_count / total) * 100.0, 2),
        nfc_match_pct=round((nfc_count / total) * 100.0, 2),
        results=results,
    )
