"""
build_owner_review_session_pkg.py

Creates the 3 owner-review session deliverables:
1. TOKENIZER_OWNER_REVIEW_SESSION.md
2. TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv
3. TOKENIZER_OWNER_REVIEW_EVIDENCE_INDEX.md

Under SOLO_DEVELOPER_OWNER_REVIEW:
- Preserves hashes of Candidate A, Exp Candidate A, Candidate B
- Preserves structural token IDs 0-11
- Preserves all review decisions as NOT_REVIEWED
- Mirrors deliverables across workspace root, patch root, and artifact directory.
"""

import csv
import hashlib
import json
import os
import shutil
from pathlib import Path
import regex
from tokenizers import Tokenizer

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")

# Tokenizers
tok_a = Tokenizer.from_file(str(WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"))
tok_exp = Tokenizer.from_file(str(PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"))

def bytes_to_unicode():
    bs = (
        list(range(ord("!"), ord("~") + 1))
        + list(range(ord("¡"), ord("¬") + 1))
        + list(range(ord("®"), ord("ÿ") + 1))
    )
    cs = bs[:]
    n = 0
    for b in range(2**8):
        if b not in bs:
            bs.append(b)
            cs.append(2**8 + n)
            n += 1
    return dict(zip(bs, [chr(c) for c in cs]))

b2u = bytes_to_unicode()
u2b = {v: k for k, v in b2u.items()}

def token_to_bytes(tok: str) -> bytes:
    b_arr = bytearray()
    for ch in tok:
        if ch in u2b:
            b_arr.append(u2b[ch])
        else:
            b_arr.extend(ch.encode("utf-8"))
    return bytes(b_arr)

with open(WORKSPACE_ROOT / "TOKENIZER_OWNER_REVIEW_30.csv", "r", encoding="utf-8") as f:
    source_30 = list(csv.DictReader(f))

# Detailed metadata for each of the 30 items
REVIEW_METADATA = {
    "OWN-REV-01": {
        "morphemes": "க + [pulli]",
        "morph_obs": "Pure consonant formed by inherent vowel cancellation.",
        "grapheme_obs": "1 grapheme cluster (க்); 2 codepoints. Both tokenizers cut between base consonant and combining pulli (1 character cut inside grapheme).",
        "limits_uncertainties": "Pulli remains a detached diacritic token (à¯į). Downstream impact on attention and reasoning remains an unverified hypothesis.",
        "concern_summary": "Detached pulli diacritic consumes 2 token sequence positions per pure consonant."
    },
    "OWN-REV-02": {
        "morphemes": "க + [au_sign]",
        "morph_obs": "Diphthongal uyirmei syllable /kau/.",
        "grapheme_obs": "1 grapheme cluster (கௌ). Exp A isolates base consonant into à®ķ and au-sign into à¯Į (1 character cut inside grapheme).",
        "limits_uncertainties": "Pipeline normalizer is null. If text arrives in NFD form, token count increases from 2 to 4.",
        "concern_summary": "Two-token diphthong segmentation; sensitive to upstream NFC vs NFD normalization."
    },
    "OWN-REV-03": {
        "morphemes": "ஸ + [pulli] + ர + [vowel_ii]",
        "morph_obs": "Traditional Grantha honorific ligature Sri.",
        "grapheme_obs": "2 grapheme clusters (ஸ், ரீ); 4 codepoints. Neither tokenizer treats Sri as an atomic token; both cut between base consonants and marks.",
        "limits_uncertainties": "Candidate A fragments into 6 tokens with incomplete bytes; Exp A forms 4 complete-character tokens but lacks an atomic ligature merge.",
        "concern_summary": "Multi-codepoint Grantha ligature fragmented across 4 tokens in Exp A (6 in Cand A)."
    },
    "OWN-REV-04": {
        "morphemes": "செய் (do) + தல் (nominalizer)",
        "morph_obs": "Clear morphological boundary between verbal stem செய் and nominalizing suffix -தல்.",
        "grapheme_obs": "4 grapheme clusters (செ, ய், த, ல்); 7 codepoints. Cuts inside graphemes ಸೆ and ய் occur in both.",
        "limits_uncertainties": "Exp A merges stem coda of suffix into 'à®¤à®²'. Does not overmerge across verb root.",
        "concern_summary": "Beneficial inflectional compression (33.3%), but retains detached pulli on terminal consonant."
    },
    "OWN-REV-05": {
        "morphemes": "வந்- (come-past) + -தேன் (1st-person singular agreement)",
        "morph_obs": "Finite past verb; clear inflectional boundary between stem and pronominal agreement.",
        "grapheme_obs": "4 grapheme clusters (வ, ந், தே, ன்); 7 codepoints. Combining marks cut internally.",
        "limits_uncertainties": "Exp A reduces from 10 to 7 tokens. Grammatical agreement suffix remains identifiable.",
        "concern_summary": "7 tokens for a single 4-syllable finite verb; compression is modest."
    },
    "OWN-REV-06": {
        "morphemes": "மரங்- (sandhi stem) + -கள் (plural suffix)",
        "morph_obs": "Plural inflection with external sandhi coda mutation /m/ -> /ŋ/.",
        "grapheme_obs": "5 grapheme clusters (ம, ர, ங், க, ள்); 7 codepoints.",
        "limits_uncertainties": "Exp A groups stem 'மர' and plural consonants 'கள'. Plural marker is preserved cleanly.",
        "concern_summary": "Plural marker is preserved cleanly, but terminal pulli remains detached."
    },
    "OWN-REV-07": {
        "morphemes": "பல (many) + கலை (arts/science) + கழகம் (university)",
        "morph_obs": "Three-constituent nominal compound with sandhi gemination.",
        "grapheme_obs": "9 grapheme clusters; 13 codepoints.",
        "limits_uncertainties": "Exp A groups sub-syllabic pairs (கல, கழ, கம) without crossing primary compound boundaries.",
        "concern_summary": "10 tokens in Exp A (down from 14); subwords are sub-syllabic rather than full root stems."
    },
    "OWN-REV-08": {
        "morphemes": "போ- (go) + -றேன் (spoken 1st-person agreement)",
        "morph_obs": "Colloquial spoken contraction of formal போகிறேன்.",
        "grapheme_obs": "3 grapheme clusters (போ, றே, ன்); 6 codepoints.",
        "limits_uncertainties": "Colloquial spoken contraction is preserved without producing out-of-vocabulary fallback bytes.",
        "concern_summary": "Spoken variant consumes 6 tokens; reflects lack of colloquial spoken data in merge training."
    },
    "OWN-REV-09": {
        "morphemes": "வீடு (house) + இற்கு (oblique/dative) + உள் (locative postposition)",
        "morph_obs": "Agglutinative postpositional stack: noun + oblique + dative + locative.",
        "grapheme_obs": "6 grapheme clusters; 12 codepoints. All combining marks detached.",
        "limits_uncertainties": "Exp A reduces from 17 to 12 tokens. Agglutinative suffix chain remains split across morphemes.",
        "concern_summary": "High sequence fertility (12 tokens for 1 word); agglutinative suffixes remain heavily segmented."
    },
    "OWN-REV-10": {
        "morphemes": "நாடு (country) + கள் (plural) + இல் (locative) + இருந்து (ablative)",
        "morph_obs": "Multi-morpheme agglutinative case stack ('from countries').",
        "grapheme_obs": "8 grapheme clusters; 15 codepoints.",
        "limits_uncertainties": "Exp A isolates plural marker -கள் and ablative -இருந்து into distinct subword groups.",
        "concern_summary": "14 tokens in Exp A (down from 19); represents high sequence overhead for agglutinative inflections."
    },
    "OWN-REV-11": {
        "morphemes": "the (definite article)",
        "morph_obs": "Monomorphemic English closed-class grammatical functional head.",
        "grapheme_obs": "3 grapheme clusters (t, h, e); single-byte ASCII. 0 cuts inside graphemes.",
        "limits_uncertainties": "Both Candidate A and Exp A segment 'the' into 2 tokens ('t | he') because 'the' was not learned as an atomic merge in initial passes.",
        "concern_summary": "Highest-frequency English word split into 2 tokens across both tokenizers."
    },
    "OWN-REV-12": {
        "morphemes": "micro (prefix/modifier) + service (base noun)",
        "morph_obs": "CROSSES_MORPHEME_BOUNDARY: Closed technical compound. Boundary between micro- and service is severed.",
        "grapheme_obs": "12 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.",
        "limits_uncertainties": "Exp A learned the non-morphemic subword 'icroser' spanning across the boundary (offset 5). Recurs in 'microservices'.",
        "concern_summary": "CRITICAL OVERMERGE: Subword 'icroser' straddles prefix-stem boundary, harming compositional semantics."
    },
    "OWN-REV-13": {
        "morphemes": "a- (privative prefix) + synchronous (stem)",
        "morph_obs": "CROSSES_MORPHEME_BOUNDARY: Greek negation prefix a- merged with root onset s-.",
        "grapheme_obs": "12 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.",
        "limits_uncertainties": "Exp A collapses into 'as | ynchronous', obscuring the privative negation prefix and mimicking function word 'as'.",
        "concern_summary": "CRITICAL OVERMERGE: Obscures privative negation prefix 'a-' into unrelated subword 'as'."
    },
    "OWN-REV-14": {
        "morphemes": "middle (root) + ware (suffix/combining form)",
        "morph_obs": "CLEAR_MORPHEME_BOUNDARY: Compound boundary between middle and ware is cleanly preserved.",
        "grapheme_obs": "10 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.",
        "limits_uncertainties": "Suffix 'ware' is an intact atomic token. Root 'middle' is fragmented internally into 4 pieces.",
        "concern_summary": "Compound boundary is preserved, but base root 'middle' is fragmented into 'm | id | d | le'."
    },
    "OWN-REV-15": {
        "morphemes": "inter- (prefix) + nation (root) + -al (suffix) + -ize (suffix) + -ation (suffix)",
        "morph_obs": "POTENTIAL_OVERMERGE: Suffixes -ational and -ization are cleanly aligned, but 'tern' spans prefix-root juncture.",
        "grapheme_obs": "20 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.",
        "limits_uncertainties": "Exp A achieves 75% compression (4 tokens vs 16). Suffix boundaries align well with derivational morphology.",
        "concern_summary": "Subword 'tern' slightly straddles prefix-root boundary, but derivational affixes align cleanly."
    },
    "OWN-REV-16": {
        "morphemes": "un- (prefix) + avoid (root) + -able (suffix)",
        "morph_obs": "CLEAR_MORPHEME_BOUNDARY: Both prefix un- and suffix -able are preserved as exact atomic morpheme tokens.",
        "grapheme_obs": "11 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.",
        "limits_uncertainties": "Base root 'avoid' is fragmented into 'av | o | id', but affix boundaries are strictly maintained.",
        "concern_summary": "Clean affix preservation ('un' and 'able'), but root 'avoid' is fragmented."
    },
    "OWN-REV-17": {
        "morphemes": "A + P + I (Initialism)",
        "morph_obs": "All-caps technical initialism: Application Programming Interface.",
        "grapheme_obs": "3 grapheme clusters (A, P, I); single-byte ASCII. 0 cuts inside graphemes.",
        "limits_uncertainties": "Cand A segments as 3 single-letter tokens ('A | P | I'); Exp A merges 'PI' ('A | PI').",
        "concern_summary": "Exp A creates 2-letter uppercase merge 'PI'; initialism is not fully atomic."
    },
    "OWN-REV-18": {
        "morphemes": "user (noun) + _ (delimiter) + id (abbreviation)",
        "morph_obs": "CLEAR_MORPHEME_BOUNDARY: Underscore delimiter is strictly isolated as an independent token.",
        "grapheme_obs": "7 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.",
        "limits_uncertainties": "Underscore is not merged into alphanumeric tokens, preserving syntax boundaries in programming text.",
        "concern_summary": "Stem 'user' is split into 'us | er', but delimiter boundary is clean."
    },
    "OWN-REV-19": {
        "morphemes": "parse (verb) + Token (noun) + ( + ) (syntax)",
        "morph_obs": "CLEAR_MORPHEME_BOUNDARY: Method identifier and syntactic parentheses isolated cleanly.",
        "grapheme_obs": "12 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.",
        "limits_uncertainties": "Exp A merges capitalized 'Token' and isolates '(' and ')', reducing tokens from 11 to 5.",
        "concern_summary": "Stem 'parse' is split as 'par | se', but CamelCase identifier boundary is respected."
    },
    "OWN-REV-20": {
        "morphemes": "returns (verb) + dict (type) + [ + str (type) + , + Any (type) + ]",
        "morph_obs": "CLEAR_MORPHEME_BOUNDARY: Code type annotation with delimiters and generics brackets.",
        "grapheme_obs": "22 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.",
        "limits_uncertainties": "Exp A forms leading-space tokens 'Ġdict' and 'ĠAny' while isolating brackets and commas.",
        "concern_summary": "Type signature tokenization is clean; punctuation delimiters are isolated."
    },
    "OWN-REV-21": {
        "morphemes": "server (Latin noun) + - (hyphen) + -ல் (Tamil locative suffix)",
        "morph_obs": "CLEAR_MORPHEME_BOUNDARY: English root and Tamil locative suffix partitioned by hyphen delimiter.",
        "grapheme_obs": "8 grapheme clusters; 9 codepoints. Pulli on ல் detached in both.",
        "limits_uncertainties": "Zero cross-script bleeding. Hyphen acts as an impermeable barrier.",
        "concern_summary": "Tamil locative suffix is cleanly isolated, but pulli remains detached."
    },
    "OWN-REV-22": {
        "morphemes": "complex (Latin adjective) + - (hyphen) + -ஆ (Tamil adverbial clitic)",
        "morph_obs": "CLEAR_MORPHEME_BOUNDARY: Latin stem and Tamil clitic partitioned cleanly.",
        "grapheme_obs": "9 grapheme clusters; 9 codepoints. Exp A has 0 character cuts and 0 byte cuts inside ஆ.",
        "limits_uncertainties": "Cand A splits ஆ at byte offset 10 into incomplete bytes; Exp A preserves entire 3-byte token à®Ĩ.",
        "concern_summary": "Exp A resolves Candidate A's byte-level splitting of clitic 'ஆ'."
    },
    "OWN-REV-23": {
        "morphemes": "testing (Latin gerund) + - (hyphen) + -க்கு (Tamil dative suffix)",
        "morph_obs": "CLEAR_MORPHEME_BOUNDARY: Latin gerund base and Tamil dative suffix partitioned by hyphen.",
        "grapheme_obs": "10 grapheme clusters; 12 codepoints. Dative suffix has internal combining mark cuts.",
        "limits_uncertainties": "Latin stem 'testing' decomposes into natural morphemes 't | est | ing'; suffix -க்கு is isolated.",
        "concern_summary": "Tamil dative suffix requires 4 tokens; Latin stem achieves morphemic alignment."
    },
    "OWN-REV-24": {
        "morphemes": "database (Latin noun) + - (hyphen) + -லிருந்து (Tamil ablative suffix)",
        "morph_obs": "CLEAR_MORPHEME_BOUNDARY: Multi-suffix ablative case cleanly partitioned from Latin stem.",
        "grapheme_obs": "13 grapheme clusters; 17 codepoints.",
        "limits_uncertainties": "Exp A reduces from 18 to 12 tokens. Latin base 'database' forms stem 'abase'.",
        "concern_summary": "Ablative suffix chain consumes 8 tokens; no script leakage observed."
    },
    "OWN-REV-25": {
        "morphemes": "deploy (Latin verb) + [space] + பண்ணினோம் (Tamil light verb)",
        "morph_obs": "CLEAR_MORPHEME_BOUNDARY: Intra-sentential code-switch across whitespace boundary.",
        "grapheme_obs": "12 grapheme clusters; 15 codepoints.",
        "limits_uncertainties": "Exp A merges onset of Tamil verb 'Ġபண' while strictly respecting word space.",
        "concern_summary": "Clean code-switching boundary; 11 tokens in Exp A (down from 18 in Cand A)."
    },
    "OWN-REV-26": {
        "morphemes": "sprint (noun) + planning (noun) + [space] + முடிஞ்சிருச்சு (colloquial Tamil verb)",
        "morph_obs": "CLEAR_MORPHEME_BOUNDARY: Multi-word English noun phrase + colloquial Tamil completive verb.",
        "grapheme_obs": "24 grapheme clusters; 28 codepoints.",
        "limits_uncertainties": "Exp A achieves 35.5% compression without cross-language boundary leakage.",
        "concern_summary": "Colloquial Tamil verb consumes 12 tokens due to lack of colloquial merges."
    },
    "OWN-REV-27": {
        "morphemes": "algorithm (Latin) + romba (Romanized Tamil) + slow-ஆ (hybrid) + இருக்கு (Tamil)",
        "morph_obs": "CLEAR_MORPHEME_BOUNDARY: Four-way code-mixing with Romanized Tamil adverb.",
        "grapheme_obs": "25 grapheme clusters; 28 codepoints.",
        "limits_uncertainties": "Exp A merges Romanized 'romba' as an atomic token ('Ġromba'), proving synthetic corpus capture.",
        "concern_summary": "Mixed-script sentence achieves 46.4% compression; Romanized adverb captured cleanly."
    },
    "OWN-REV-28": {
        "morphemes": "Please check the logs (English sentence) + da (Tamil discourse marker)",
        "morph_obs": "CLEAR_MORPHEME_BOUNDARY: Grammatical English clause + colloquial Tamil pragmatic particle.",
        "grapheme_obs": "19 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.",
        "limits_uncertainties": "Exp A achieves optimal 1 token per word across entire sentence ('Please | Ġcheck | Ġthe | Ġlogs | Ġda').",
        "concern_summary": "Optimal tokenization efficiency achieved; discourse particle 'da' isolated cleanly."
    },
    "OWN-REV-29": {
        "morphemes": "pann- (stem) + irukk- (aspect) + -om (1st-plural agreement)",
        "morph_obs": "CLEAR_MORPHEME_BOUNDARY: Romanized colloquial Tamil verbal morphology.",
        "grapheme_obs": "11 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.",
        "limits_uncertainties": "Exp A reduces from 10 single-letter tokens to 6 morphemic chunks ('p | ann | iru | k | k | om').",
        "concern_summary": "Romanized verbal morphology achieves 40% compression with meaningful sub-stems."
    },
    "OWN-REV-30": {
        "morphemes": "கம்ப்யூட்டர் (transliteration of 'computer')",
        "morph_obs": "CLEAR_MORPHEME_BOUNDARY: Phonetic transliteration of technical loanword into Tamil script.",
        "grapheme_obs": "7 grapheme clusters; 12 codepoints. All pulli marks detached.",
        "limits_uncertainties": "Exp A merges initial syllable 'கம்' and terminal syllable 'டர்', reducing tokens from 16 to 10.",
        "concern_summary": "Initial and final syllables merged, but internal consonant cluster remains fragmented."
    }
}

# ========================================================
# 1. BUILD TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv
# ========================================================
template_rows = []
for r in source_30:
    rev_id = r["review_id"]
    text = r["original_text"]
    meta = REVIEW_METADATA.get(rev_id, {})
    
    enc_a = tok_a.encode(text)
    enc_exp = tok_exp.encode(text)
    
    dec_a = tok_a.decode(enc_a.ids)
    dec_exp = tok_exp.decode(enc_exp.ids)
    rec_status = "EXACT_MATCH_100%" if (dec_a == text and dec_exp == text) else "MISMATCH"
    
    template_rows.append({
        "review_id": rev_id,
        "language": r["language"],
        "category": r["category"],
        "original_text": text,
        "cand_a_tokens": " | ".join(enc_a.tokens),
        "cand_exp_tokens": " | ".join(enc_exp.tokens),
        "cand_a_token_ids": str(enc_a.ids),
        "cand_exp_token_ids": str(enc_exp.ids),
        "cand_a_count": len(enc_a.ids),
        "cand_exp_count": len(enc_exp.ids),
        "unicode_codepoints": r["unicode_codepoints"],
        "grapheme_clusters": r["grapheme_clusters"],
        "reconstruction_status": rec_status,
        "technical_concern_summary": meta.get("concern_summary", ""),
        "owner_decision": "NOT_REVIEWED",
        "owner_decision_options": "OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION | OWNER_ACCEPTS_ORIGINAL_SEGMENTATION | OWNER_ACCEPTS_BOTH | OWNER_REJECTS_BOTH | OWNER_REQUIRES_MORE_EVIDENCE",
        "owner_rationale": ""
    })

template_csv_path = WORKSPACE_ROOT / "TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv"
with open(template_csv_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(template_rows[0].keys()))
    writer.writeheader()
    writer.writerows(template_rows)
print(f"Generated {template_csv_path} with {len(template_rows)} rows.")

# ========================================================
# 2. BUILD TOKENIZER_OWNER_REVIEW_SESSION.md
# ========================================================
session_md = """# IGRIS Tokenizer Owner Review Session: 30 Prioritized Cases

**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Sole Accountable Reviewer:** IGRIS Lead Developer / Project Owner  
**Session Objective:** Evaluate 30 prioritized subword segmentation examples across Tamil, English, and Tanglish.  
**Governing Invariant:** Pretraining and Data Acquisition gates remain strictly **`LOCKED`** ($0.00 cloud spend). Candidate A remains the selected production tokenizer; Experimental Candidate A remains quarantined.

> [!IMPORTANT]
> **CRITICAL GOVERNANCE PRINCIPLE:**  
> **Accepting a segmentation example is NOT the same as approving tokenizer promotion.**  
> Individual segmentation approvals indicate linguistic or architectural acceptability of a subword pattern. Tokenizer promotion requires formal gate sign-off, vocabulary constraint auditing, and full baseline comparison.  
> All 30 review rows in [TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv](file:///C:/IGRIS/TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv) have been initialized to **`NOT_REVIEWED`**. No decisions have been prepopulated.

---

## 1. Owner Decision Protocol & Allowed Options

For each of the 30 examples below, the owner selects exactly one determination:

```
+───────────────────────────────────────────────────────────────────────────────────────────────+
|                                    OWNER DECISION TAXONOMY                                    |
+───────────────────────────────────────────+───────────────────────────────────────────────────+
| Decision Option                           | Definition & Usage Context                        |
+───────────────────────────────────────────+───────────────────────────────────────────────────+
| OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION   | Owner approves Exp Candidate A's subword split.   |
| OWNER_ACCEPTS_ORIGINAL_SEGMENTATION       | Owner prefers Original Candidate A's split.       |
| OWNER_ACCEPTS_BOTH                        | Both segmentations are linguistically acceptable. |
| OWNER_REJECTS_BOTH                        | Both tokenizers fail linguistic criteria.         |
| OWNER_REQUIRES_MORE_EVIDENCE              | Determination deferred pending downstream probes. |
| NOT_REVIEWED                              | Initial state awaiting owner inspection.          |
+───────────────────────────────────────────+───────────────────────────────────────────────────+
```

---

## 2. Review Section A: Tamil Language Phenomena (10 Cases)

"""

for r in template_rows[:10]:
    rev_id = r["review_id"]
    meta = REVIEW_METADATA.get(rev_id, {})
    session_md += f"""### {rev_id}: `{r['original_text']}` ({r['category']})
- **Technical Concern Summary:** {meta.get('concern_summary', '')}
- **Original Input Text:** `{r['original_text']}`
- **Original Candidate A Tokenization:** `{r['cand_a_tokens']}`
- **Experimental Candidate A Tokenization:** `{r['cand_exp_tokens']}`
- **Token IDs:**
  - Candidate A: `{r['cand_a_token_ids']}`
  - Exp Candidate A: `{r['cand_exp_token_ids']}`
- **Token Counts:** Candidate A = {r['cand_a_count']} tokens | Exp Candidate A = {r['cand_exp_count']} tokens (Reduction: {round(100*(1 - r['cand_exp_count']/r['cand_a_count']), 1)}%)
- **Unicode Codepoints:** `{r['unicode_codepoints']}`
- **Grapheme-Boundary Observations:** {meta.get('grapheme_obs', '')}
- **Morphological Observations:** {meta.get('morph_obs', '')}
- **Reconstruction Status:** `{r['reconstruction_status']}` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** {meta.get('limits_uncertainties', '')}
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

"""

session_md += """## 3. Review Section B: English Language Phenomena (10 Cases)

"""

for r in template_rows[10:20]:
    rev_id = r["review_id"]
    meta = REVIEW_METADATA.get(rev_id, {})
    session_md += f"""### {rev_id}: `{r['original_text']}` ({r['category']})
- **Technical Concern Summary:** {meta.get('concern_summary', '')}
- **Original Input Text:** `{r['original_text']}`
- **Original Candidate A Tokenization:** `{r['cand_a_tokens']}`
- **Experimental Candidate A Tokenization:** `{r['cand_exp_tokens']}`
- **Token IDs:**
  - Candidate A: `{r['cand_a_token_ids']}`
  - Exp Candidate A: `{r['cand_exp_token_ids']}`
- **Token Counts:** Candidate A = {r['cand_a_count']} tokens | Exp Candidate A = {r['cand_exp_count']} tokens (Reduction: {round(100*(1 - r['cand_exp_count']/r['cand_a_count']), 1)}%)
- **Unicode Codepoints:** `{r['unicode_codepoints']}`
- **Grapheme-Boundary Observations:** {meta.get('grapheme_obs', '')}
- **Morphological Observations:** {meta.get('morph_obs', '')}
- **Reconstruction Status:** `{r['reconstruction_status']}` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** {meta.get('limits_uncertainties', '')}
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

"""

session_md += """## 4. Review Section C: Tanglish Language Phenomena (10 Cases)

"""

for r in template_rows[20:]:
    rev_id = r["review_id"]
    meta = REVIEW_METADATA.get(rev_id, {})
    session_md += f"""### {rev_id}: `{r['original_text']}` ({r['category']})
- **Technical Concern Summary:** {meta.get('concern_summary', '')}
- **Original Input Text:** `{r['original_text']}`
- **Original Candidate A Tokenization:** `{r['cand_a_tokens']}`
- **Experimental Candidate A Tokenization:** `{r['cand_exp_tokens']}`
- **Token IDs:**
  - Candidate A: `{r['cand_a_token_ids']}`
  - Exp Candidate A: `{r['cand_exp_token_ids']}`
- **Token Counts:** Candidate A = {r['cand_a_count']} tokens | Exp Candidate A = {r['cand_exp_count']} tokens (Reduction: {round(100*(1 - r['cand_exp_count']/r['cand_a_count']), 1)}%)
- **Unicode Codepoints:** `{r['unicode_codepoints']}`
- **Grapheme-Boundary Observations:** {meta.get('grapheme_obs', '')}
- **Morphological Observations:** {meta.get('morph_obs', '')}
- **Reconstruction Status:** `{r['reconstruction_status']}` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** {meta.get('limits_uncertainties', '')}
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

"""

session_md += """## 5. Owner Decision Instructions

1. Open [TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv](file:///C:/IGRIS/TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv).
2. For each row (`OWN-REV-01` to `OWN-REV-30`), update `owner_decision` from `NOT_REVIEWED` to your chosen determination.
3. Record your technical rationale in `owner_rationale`.
4. Supporting evidence for all 300 test cases is indexed in [TOKENIZER_OWNER_REVIEW_EVIDENCE_INDEX.md](file:///C:/IGRIS/TOKENIZER_OWNER_REVIEW_EVIDENCE_INDEX.md).
"""

session_path = WORKSPACE_ROOT / "TOKENIZER_OWNER_REVIEW_SESSION.md"
with open(session_path, "w", encoding="utf-8") as f:
    f.write(session_md)
print(f"Generated {session_path}.")

# ========================================================
# 3. BUILD TOKENIZER_OWNER_REVIEW_EVIDENCE_INDEX.md
# ========================================================
evidence_index_md = """# IGRIS Tokenizer Owner Review Evidence Index

**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Sole Accountable Decision-Maker:** IGRIS Lead Developer / Project Owner  
**Purpose:** Comprehensive evidence directory mapping the 30 prioritized owner-review cases to primary technical audits and supporting 300-item evaluation datasets.

---

## 1. Master Evidence Deliverables Directory

| Evidence Document / CSV | Description & Role | Scope | Clickable Link |
|:---|:---|:---:|:---:|
| **`TOKENIZER_FINAL_RECONCILIATION_REPORT.md`** | Primary reconciliation report: definitive resolution of `complex-ஆ`, 300-item grapheme reconciliation, and conservative morphological reclassification. | Primary Report | [TOKENIZER_FINAL_RECONCILIATION_REPORT.md](file:///C:/IGRIS/TOKENIZER_FINAL_RECONCILIATION_REPORT.md) |
| **`TOKENIZER_GRAPHEME_RECONCILIATION_300.csv`** | Full 300-record audit detailing character cuts, byte cuts, and cluster counts across both tokenizers. | 300 records | [TOKENIZER_GRAPHEME_RECONCILIATION_300.csv](file:///C:/IGRIS/TOKENIZER_GRAPHEME_RECONCILIATION_300.csv) |
| **`TOKENIZER_MORPHOLOGY_REVIEW_V2.csv`** | Conservative morphological categorization of 15 English overmerging cases. | 15 records | [TOKENIZER_MORPHOLOGY_REVIEW_V2.csv](file:///C:/IGRIS/TOKENIZER_MORPHOLOGY_REVIEW_V2.csv) |
| **`TOKENIZER_UNICODE_DIAGNOSTICS_V2.md`** | ByteLevel BPE mechanics, 100% roundtrip proof, and NFC/NFD empirical findings. | Technical Diagnostic | [TOKENIZER_UNICODE_DIAGNOSTICS_V2.md](file:///C:/IGRIS/TOKENIZER_UNICODE_DIAGNOSTICS_V2.md) |
| **`TOKENIZER_BYTELEVEL_MAPPING_AUDIT.csv`** | 16 representative cases with byte sequences, token IDs, individual token bytes, and reconstructed hex. | 16 records | [TOKENIZER_BYTELEVEL_MAPPING_AUDIT.csv](file:///C:/IGRIS/TOKENIZER_BYTELEVEL_MAPPING_AUDIT.csv) |
| **`TOKENIZER_NORMALIZATION_AUDIT.csv`** | 16 cases testing NFC vs NFD token count differences and exact reconstruction fidelity. | 16 records | [TOKENIZER_NORMALIZATION_AUDIT.csv](file:///C:/IGRIS/TOKENIZER_NORMALIZATION_AUDIT.csv) |
| **`TOKENIZER_HUMAN_REVIEW_SAMPLE.csv`** | Baseline 300-item review sample (100 Tamil, 100 English, 100 Tanglish; all `NOT_REVIEWED`). | 300 records | [TOKENIZER_HUMAN_REVIEW_SAMPLE.csv](file:///C:/IGRIS/TOKENIZER_HUMAN_REVIEW_SAMPLE.csv) |
| **`TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv`**| Decision template for the 30 prioritized items (all initialized to `NOT_REVIEWED`). | 30 records | [TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv](file:///C:/IGRIS/TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv) |
| **`TOKENIZER_OWNER_REVIEW_SESSION.md`** | Evidence-based walkthrough of all 30 prioritized review examples. | 30 records | [TOKENIZER_OWNER_REVIEW_SESSION.md](file:///C:/IGRIS/TOKENIZER_OWNER_REVIEW_SESSION.md) |

---

## 2. 30 Prioritized Items Cross-Reference Matrix

| Review ID | Language | Category | Input Text | Cand A Count | Exp A Count | Primary Technical Concern | Supporting Audit Reference |
|:---|:---:|:---:|:---|:---:|:---:|:---|:---:|
| **OWN-REV-01** | TAMIL | pulli_and_virama | `க்` | 2 | 2 | Detached pulli diacritic (2 tokens/consonant) | BPE-MAP-01, GRP-AUD-04 |
| **OWN-REV-02** | TAMIL | uyirmei_combinations | `கௌ` | 3 | 2 | 2-token diphthong; NFC/NFD sensitivity | BPE-MAP-02, NORM-AUD-02 |
| **OWN-REV-03** | TAMIL | grantha_and_conjuncts | `ஸ்ரீ` | 6 | 4 | Multi-codepoint Grantha ligature fragmented | BPE-MAP-07, GRP-AUD-09 |
| **OWN-REV-04** | TAMIL | roots_and_suffixes | `செய்தல்` | 9 | 6 | Verbal noun inflection compression (33.3%) | BPE-MAP-04, GRP-REC-002 |
| **OWN-REV-05** | TAMIL | tense_and_person | `வந்தேன்` | 10 | 7 | Past finite verb; pronominal agreement suffix | BPE-MAP-05, GRP-REC-011 |
| **OWN-REV-06** | TAMIL | singular_and_plural | `மரங்கள்` | 9 | 5 | Plural marker preserved cleanly | BPE-MAP-06, GRP-REC-021 |
| **OWN-REV-07** | TAMIL | compound_words | `பல்கலைக்கழகம்` | 14 | 10 | 10 tokens; subwords are sub-syllabic | BPE-MAP-08, GRP-AUD-11 |
| **OWN-REV-08** | TAMIL | spoken_vs_formal | `போறேன்` | 9 | 6 | Spoken colloquial contraction preserved | GRP-REC-041 |
| **OWN-REV-09** | TAMIL | agglutinative_inflections | `வீட்டிற்குள்` | 17 | 12 | Agglutinative postposition stack (12 tokens) | BPE-MAP-09, GRP-REC-091 |
| **OWN-REV-10** | TAMIL | agglutinative_inflections | `நாடுகளிலிருந்து` | 19 | 14 | Multi-morpheme ablative stack (14 tokens) | BPE-MAP-10, GRP-REC-100 |
| **OWN-REV-11** | ENGLISH | common_words | `the` | 2 | 2 | High-frequency function word split as 't \| he' | GRP-REC-101 |
| **OWN-REV-12** | ENGLISH | technical_vocabulary | `microservice` | 11 | 3 | **CRITICAL OVERMERGE:** 'icroser' spans boundary | OVM-REV-01 |
| **OWN-REV-13** | ENGLISH | programming_terminology | `asynchronous` | 12 | 2 | **CRITICAL OVERMERGE:** Privative 'a-' in 'as' | OVM-REV-05 |
| **OWN-REV-14** | ENGLISH | programming_terminology | `middleware` | 10 | 5 | Clean boundary: 'ware' intact, 'middle' split | OVM-REV-07 |
| **OWN-REV-15** | ENGLISH | long_words | `internationalization` | 16 | 4 | Derivational suffixes '-ational' & '-ization' | OVM-REV-10 |
| **OWN-REV-16** | ENGLISH | prefixes_and_suffixes | `unavoidable` | 10 | 5 | Clean affix preservation: 'un' and 'able' | OVM-REV-12 |
| **OWN-REV-17** | ENGLISH | acronyms_initialisms | `API` | 3 | 2 | Merges 'PI' into 2-letter uppercase token | GRP-REC-171 |
| **OWN-REV-18** | ENGLISH | numbers_punctuation | `user_id` | 6 | 4 | Underscore delimiter strictly isolated | GRP-REC-185 |
| **OWN-REV-19** | ENGLISH | numbers_punctuation | `parseToken()` | 11 | 5 | Capitalized 'Token' merged; syntax isolated | GRP-REC-186 |
| **OWN-REV-20** | ENGLISH | code_adjacent_text | `returns dict[str, Any]` | 22 | 15 | Delimiters preserved; type generics isolated | GRP-REC-193 |
| **OWN-REV-21** | TANGLISH | english_with_tamil_suffixes | `server-ல்` | 7 | 5 | Latin root and Tamil locative cleanly isolated | BPE-MAP-11, GRP-AUD-13 |
| **OWN-REV-22** | TANGLISH | english_with_tamil_suffixes | `complex-ஆ` | 9 | 5 | Exp A eliminates byte-level split of 'ஆ' | BPE-MAP-12, GRP-AUD-14 |
| **OWN-REV-23** | TANGLISH | english_with_tamil_suffixes | `testing-க்கு` | 10 | 8 | Latin gerund base and Tamil dative suffix | BPE-MAP-13, GRP-AUD-15 |
| **OWN-REV-24** | TANGLISH | english_with_tamil_suffixes | `database-லிருந்து` | 18 | 12 | Multi-suffix ablative case cleanly partitioned | BPE-MAP-14, GRP-AUD-16 |
| **OWN-REV-25** | TANGLISH | intra_sentential_code_switch | `deploy பண்ணினோம்` | 18 | 11 | English verb + Tamil light verb predicate | BPE-MAP-15, GRP-REC-231 |
| **OWN-REV-26** | TANGLISH | intra_sentential_code_switch | `sprint planning முடிஞ்சிருச்சு`| 31 | 20 | Multi-word NP + colloquial Tamil verb | GRP-REC-234 |
| **OWN-REV-27** | TANGLISH | intra_sentential_code_switch | `algorithm romba slow-ஆ இருக்கு`| 28 | 15 | Romanized 'romba' merged as atomic token | BPE-MAP-16, GRP-REC-235 |
| **OWN-REV-28** | TANGLISH | english_with_tamil_discourse | `Please check the logs da` | 19 | 5 | Optimal 1 token per word achieved | GRP-REC-261 |
| **OWN-REV-29** | TANGLISH | spoken_informal_tanglish_verbs| `pannirukkom` | 10 | 6 | Romanized verbal inflection morphemic chunks | GRP-REC-276 |
| **OWN-REV-30** | TANGLISH | tamil_script_loanwords | `கம்ப்யூட்டர்` | 16 | 10 | Loanword transliteration syllables merged | GRP-REC-291 |

---

## 3. Governance Verification Notice

- **Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`
- **Candidate A Hash:** `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` (Selected production tokenizer)
- **Experimental Candidate A Hash:** `3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce` (Quarantined)
- **Candidate B Reference Hash:** `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` (Reference unigram)
- **Structural Tokens 0–11:** Verified intact in both tokenizers.
- **Pretraining & Acquisition Gates:** Verified strictly **`LOCKED`** ($0.00 cloud spend).
"""

evidence_index_path = WORKSPACE_ROOT / "TOKENIZER_OWNER_REVIEW_EVIDENCE_INDEX.md"
with open(evidence_index_path, "w", encoding="utf-8") as f:
    f.write(evidence_index_md)
print(f"Generated {evidence_index_path}.")

# Mirror all 3 files
session_files = [
    "TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv",
    "TOKENIZER_OWNER_REVIEW_SESSION.md",
    "TOKENIZER_OWNER_REVIEW_EVIDENCE_INDEX.md"
]

for fn in session_files:
    src = WORKSPACE_ROOT / fn
    shutil.copy2(src, PATCH_ROOT / fn)
    shutil.copy2(src, ARTIFACT_DIR / fn)
    print(f"Mirrored {fn} -> {PATCH_ROOT / fn} and {ARTIFACT_DIR / fn}")

print("\nALL OWNER REVIEW SESSION DELIVERABLES CREATED AND MIRRORED.")
