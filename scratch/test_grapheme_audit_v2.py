import regex
from tokenizers import Tokenizer

tok_a = Tokenizer.from_file(r"C:\IGRIS\artifacts\tokenizer\candidate_a\tokenizer.json")
tok_exp = Tokenizer.from_file(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_a_synthetic_experiment\tokenizer.json")

test_cases = [
    ("க", "tamil_consonant", "Base consonant ka", ["க"]),
    ("ி", "tamil_vowel_sign", "Combining vowel sign i", ["ி"]),
    ("்", "tamil_pulli", "Combining virama / pulli", ["்"]),
    ("க்", "tamil_uyirmei_pure", "Pure consonant ka + pulli", ["க", "[pulli]"]),
    ("தி", "tamil_uyirmei_vocalized", "Syllable ta + vowel sign i", ["த", "[vowel_i]"]),
    ("பூ", "tamil_uyirmei_vocalized", "Syllable pa + vowel sign uu", ["ப", "[vowel_uu]"]),
    ("கை", "tamil_uyirmei_vocalized", "Syllable ka + vowel sign ai", ["க", "[vowel_ai]"]),
    ("கௌ", "tamil_uyirmei_diphthong", "Syllable ka + diphthong au", ["க", "[vowel_au]"]),
    ("ஸ்ரீ", "grantha_ligature", "Grantha conjunct sa + pulli + ra + vowel ii", ["ஸ", "[pulli]", "ர", "[vowel_ii]"]),
    ("க்ஷ", "grantha_conjunct", "Grantha conjunct ka + pulli + sha", ["க", "[pulli]", "ஷ"]),
    ("பல்கலைக்கழகம்", "tamil_compound", "Nominal compound: பல + கலை + கழகம்", ["பல", "கலை", "கழகம்"]),
    ("மணிக்கூண்டு", "tamil_compound", "Nominal compound: மணி + கூண்டு", ["மணி", "கூண்டு"]),
    ("server-ல்", "tanglish_suffix", "Latin noun + hyphen + Tamil locative -ல்", ["server", "-", "ல்"]),
    ("complex-ஆ", "tanglish_suffix", "Latin adjective + hyphen + Tamil clitic -ஆ", ["complex", "-", "ஆ"]),
    ("testing-க்கு", "tanglish_suffix", "Latin gerund + hyphen + Tamil dative -க்கு", ["testing", "-", "க்கு"]),
    ("database-லிருந்து", "tanglish_suffix", "Latin noun + hyphen + Tamil ablative -லிருந்து", ["database", "-", "லிருந்து"])
]

print("=== GRAPHEME & BOUNDARY HIERARCHY ANALYSIS ===")
for text, ltype, desc, morphemes in test_cases:
    enc_a = tok_a.encode(text)
    enc_exp = tok_exp.encode(text)
    
    raw_bytes = text.encode("utf-8")
    codepoints = [f"U+{ord(c):04X}" for c in text]
    graphemes = regex.findall(r"\X", text)
    
    # Analyze token offsets against boundaries
    offsets_a = enc_a.offsets
    offsets_exp = enc_exp.offsets
    
    # Grapheme spans
    g_spans = []
    curr = 0
    for g in graphemes:
        g_spans.append((curr, curr + len(g), g))
        curr += len(g)
        
    cuts_a = set(end for start, end in offsets_a if 0 < end < len(text))
    cuts_exp = set(end for start, end in offsets_exp if 0 < end < len(text))
    
    internal_g_cuts_a = [g for start, end, g in g_spans if any(start < c < end for c in cuts_a)]
    internal_g_cuts_exp = [g for start, end, g in g_spans if any(start < c < end for c in cuts_exp)]
    
    print(f"\nSample: {text!r} ({ltype})")
    print(f"  Counts: Bytes={len(raw_bytes)}, CPs={len(codepoints)}, Graphemes={len(graphemes)}, Morphemes={len(morphemes)}")
    print(f"  Cand A: {enc_a.tokens} | Internal Grapheme Cuts: {internal_g_cuts_a}")
    print(f"  Exp A : {enc_exp.tokens} | Internal Grapheme Cuts: {internal_g_cuts_exp}")
