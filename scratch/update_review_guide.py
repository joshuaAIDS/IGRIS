"""
update_review_guide.py

Updates TOKENIZER_OWNER_REVIEW_GUIDE.md to correct speculative claims and incorporate:
1. Four distinct boundary levels (Byte, Codepoint, Grapheme Cluster, Morpheme).
2. Clarification of ByteLevel BPE token properties (individual tokens need not be complete UTF-8).
3. Explicit classification of hypotheses vs established facts.
4. Specific empirical overmerging findings from TOKENIZER_OVERMERGING_AUDIT.csv.
5. Integration with the V2 diagnostics and audit CSVs.
"""

from pathlib import Path
import shutil

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")

guide_content = """# IGRIS Tokenizer Owner Review Guide: 30 Prioritized Linguistic Segmentation Cases (V2)

**Document Status:** AUTHORITATIVE OWNER REVIEW MANUAL (VERSION 2.0)  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Sole Decision-Maker:** IGRIS Lead Developer / Project Owner  
**Audit Context:** Linguistic Segmentation Quality Audit returned `SEGMENTATION_CONDITIONAL`  
**Governing Invariant:** Pretraining and Acquisition Gates are `LOCKED` ($0.00 cloud spend). Candidate A remains selected; Exp Candidate A remains quarantined.

---

## 1. Purpose & How to Use This Guide

This review guide provides the sole developer and project owner with the complete linguistic, morphological, and computational context required to evaluate the **30 prioritized segmentation cases** in `TOKENIZER_OWNER_REVIEW_30.csv`.

### Review Protocol:
1. Open [TOKENIZER_OWNER_REVIEW_30.csv](file:///C:/IGRIS/TOKENIZER_OWNER_REVIEW_30.csv).
2. For each row (`OWN-REV-01` to `OWN-REV-30`), inspect the side-by-side tokenization of **Candidate A** vs **Experimental Candidate A**.
3. Consult the detailed breakdown for that row in this guide.
4. Cross-reference specialized audits as needed:
   - [TOKENIZER_UNICODE_DIAGNOSTICS_V2.md](file:///C:/IGRIS/TOKENIZER_UNICODE_DIAGNOSTICS_V2.md) for ByteLevel mapping mechanics.
   - [TOKENIZER_BYTELEVEL_MAPPING_AUDIT.csv](file:///C:/IGRIS/TOKENIZER_BYTELEVEL_MAPPING_AUDIT.csv) for exact byte-by-byte reconstruction tables.
   - [TOKENIZER_GRAPHEME_BOUNDARY_AUDIT.csv](file:///C:/IGRIS/TOKENIZER_GRAPHEME_BOUNDARY_AUDIT.csv) for 4-tier boundary comparisons.
   - [TOKENIZER_NORMALIZATION_AUDIT.csv](file:///C:/IGRIS/TOKENIZER_NORMALIZATION_AUDIT.csv) for NFC vs NFD empirical tests.
   - [TOKENIZER_OVERMERGING_AUDIT.csv](file:///C:/IGRIS/TOKENIZER_OVERMERGING_AUDIT.csv) for morphological boundary cross-merge audits.
5. When ready to record an owner determination, edit `human_review_decision` from `NOT_REVIEWED` to one of the approved decision options, and record your reasoning in `reviewer_rationale`.

> [!WARNING]
> In accordance with project governance, all rows in `TOKENIZER_OWNER_REVIEW_30.csv` and `TOKENIZER_HUMAN_REVIEW_SAMPLE.csv` have been delivered as `NOT_REVIEWED`.  
> Only the project owner may transition these statuses.

---

## 2. Decision Framework & Boundary Hierarchy Rubric

When evaluating subword merges in Candidate A and Experimental Candidate A, apply this four-tier boundary model:

```
+───────────────────────────────────────────────────────────────────────────────────────────────+
|                                HIERARCHY OF SEGMENTATION BOUNDARIES                           |
+───────────────────────────────+───────────────────────────────────────────────────────────────+
| Boundary Tier                 | Technical Definition & Evaluation Context                     |
+───────────────────────────────+───────────────────────────────────────────────────────────────+
| 1. Byte Boundary              | Division between raw 8-bit octets in UTF-8 (e.g. 0xE0 | 0xAE). |
|                               | Individual BPE tokens do NOT need to contain complete UTF-8.  |
| 2. Unicode Code-Point         | Division between atomic Unicode scalar values (U+0B95 | U+0BCD)|
| 3. Grapheme-Cluster           | Division between perceived orthographic syllables (UAX #29 \\X)|
| 4. Linguistic Morpheme        | Division between semantic/grammatical units (root + affix).   |
+───────────────────────────────+───────────────────────────────────────────────────────────────+
```

### Critical Architectural Clarifications:
- **ByteLevel BPE Contract:** Individual BPE tokens represent sequences of bytes. They are not required to form valid independent Unicode scalar values. Full-sequence decoding reconstructs the original string with 100.0% fidelity.
- **Lower Fertility vs Segmentation Quality:** Lower token count measures sequence compression. It does *not* automatically indicate linguistically superior segmentation. Uncontrolled compression produces overmerges that destroy compositional generalization.
- **Pulli Detachment:** Isolating virama/pulli as a detached diacritic token (`à¯į`) allows subword sharing between pure consonants and vocalized syllables, but doubles sequence length for consonant clusters. Whether this improves or impairs grammatical reasoning in language models is an **open hypothesis** requiring empirical downstream pretraining validation.

### Approved Decision Options:
- **`ACCEPT_MERGE`**: The merge forms a valid morpheme, syllable, or natural multi-character cluster that improves token fertility without semantic corruption.
- **`FLAG_NON_MORPHEMIC`**: The merge spans across an essential morphological boundary, creating a subword that breaks grammatical recognizability (e.g. `microservice` $\\to$ `m | icroser | vice`).
- **`FLAG_OVERFRAGMENTED`**: The tokenization is excessively fragmented into single characters or orphan bytes, imposing high self-attention quadratic overhead.
- **`FLAG_CODE_SWITCH_BOUNDARY`**: The tokenizer failed to cleanly partition Latin script from Tamil script in Tanglish text.
- **`REJECT_MERGE`**: The merge is detrimental and must be eliminated during future vocabulary retraining.

---

## 3. Detailed Walkthrough of the 30 Prioritized Cases

### SECTION A: TAMIL PHENOMENA (OWN-REV-01 TO OWN-REV-10)

#### OWN-REV-01: `க்` (Atomic Consonant with Pulli)
- **Category:** `pulli_and_virama`
- **Candidate A:** `à®ķ | à¯į` (2 tokens)
- **Exp Candidate A:** `à®ķ | à¯į` (2 tokens)
- **Token Reduction:** 0.0% (Identical)
- **Unicode Codepoints:** `U+0B95 U+0BCD` (2 codepoints)
- **Grapheme Clusters:** `க்` (1 grapheme cluster)
- **Linguistic Analysis:** In Tamil, `க்` represents the voiceless velar stop /k/ with the inherent vowel /a/ silenced by virama (pulli). Both tokenizers cut between `U+0B95` and `U+0BCD`. This cut respects code-point and morpheme boundaries, but splits the single grapheme cluster.
- **Epistemic Status:** Detached pulli allows the subword vocabulary to share representations between pure consonants (`க்`) and vocalized syllables (`க`, `கி`), but whether this improves grammatical reasoning or unnecessarily inflates sequence length is an **unsupported hypothesis** requiring downstream empirical pretraining probes.
- **Owner Options:** `ACCEPT_MERGE` (maintain current standard) or `FLAG_OVERFRAGMENTED` (if atomic uyirmei tokens are desired in future).

#### OWN-REV-02: `கௌ` (Uyirmei Diphthong AU)
- **Category:** `uyirmei_combinations`
- **Candidate A:** `à®ķ | à¯ | Į` (3 tokens)
- **Exp Candidate A:** `à®ķ | à¯Į` (2 tokens)
- **Token Reduction:** 33.3%
- **Unicode Codepoints:** `U+0B95 U+0BCC` (in NFC: 2 codepoints)
- **Grapheme Clusters:** `கௌ` (1 grapheme cluster)
- **Linguistic Analysis:** Diphthongal vowel uyirmei /kau/. Candidate A splits the base consonant and vowel sign into orphan byte fragments, whereas Exp Candidate A groups the base consonant into `à®ķ` and the au-sign into `à¯Į`.
- **Pipeline Normalizer Note:** `tokenizer.json` has `normalizer: null`. If text arrives in NFD form (`U+0B95 U+0BC6 U+0BD7`), Exp A produces 4 tokens. Upstream NFC normalization is strongly recommended.
- **Owner Options:** `ACCEPT_MERGE; ENFORCE_NFC; FLAG_OVERFRAGMENTED`.

#### OWN-REV-03: `ஸ்ரீ` (Grantha Ligature Sri)
- **Category:** `grantha_and_conjuncts`
- **Candidate A:** `à® | ¸ | à¯į | à®° | à¯ | Ģ` (6 tokens)
- **Exp Candidate A:** `à®¸ | à¯į | à®° | à¯Ģ` (4 tokens)
- **Token Reduction:** 33.3%
- **Unicode Codepoints:** `U+0BB8 U+0BCD U+0BB0 U+0BC0` (4 codepoints)
- **Grapheme Clusters:** `ஸ் | ரீ` (2 grapheme clusters)
- **Linguistic Analysis:** Grantha honorific ligature Sri. Exp Candidate A merges orphan bytes into valid characters (`ஸ`, `்`, `ர`, `ீ`), eliminating byte fragmentation.
- **Owner Options:** `ACCEPT_MERGE; FLAG_OVERFRAGMENTED; ADD_ATOMIC_LIGATURE`.

#### OWN-REV-04: `செய்தல்` (Root + Verbal Noun Suffix)
- **Category:** `roots_and_suffixes`
- **Candidate A:** `à® | ļ | à¯ | Ĩ | à®¯ | à¯į | à®¤ | à®² | à¯į` (9 tokens)
- **Exp Candidate A:** `à®ļ | à¯Ĩ | à®¯ | à¯į | à®¤à®² | à¯į` (6 tokens)
- **Token Reduction:** 33.3%
- **Unicode Codepoints:** `U+0B9A U+0BC6 U+0BAF U+0BCD U+0BA4 U+0BB2 U+0BCD`
- **Grapheme Clusters:** `செ | ய் | த | ல்` (4 clusters)
- **Linguistic Analysis:** Verbal noun formation: root verb `செய்` (do) + nominalizing suffix `-தல்` (doing/action). Exp Candidate A merges `à®¤à®²` (the consonant stems of `-தல்`), aligning well with Tamil derivational morphology.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_INFLECTION_SPLIT`.

#### OWN-REV-05: `வந்தேன்` (Past Tense + 1st Person Singular)
- **Category:** `tense_and_person`
- **Candidate A:** `à® | µ | à® | ¨ | à¯į | à®¤ | à¯ | ĩ | à®© | à¯į` (10 tokens)
- **Exp Candidate A:** `à®µ | à®¨ | à¯į | à®¤ | à¯ĩ | à®© | à¯į` (7 tokens)
- **Token Reduction:** 30.0%
- **Unicode Codepoints:** `U+0BB5 U+0BA8 U+0BCD U+0BA4 U+0BC7 U+0BA9 U+0BCD`
- **Grapheme Clusters:** `வ | ந் | தே | ன்` (4 clusters)
- **Linguistic Analysis:** Past tense finite verb: root `வந்-` + past tense `த்` + agreement suffix `-ஏன்` ("I came"). Exp Candidate A removes all orphan byte splits. The grammatical junction between stem and suffix remains learnable.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_TENSE_SPLIT`.

#### OWN-REV-06: `மரங்கள்` (Root + Plural Suffix)
- **Category:** `singular_and_plural`
- **Candidate A:** `à®® | à®° | à® | Ļ | à¯į | à®ķ | à® | ³ | à¯į` (9 tokens)
- **Exp Candidate A:** `à®®à®° | à®Ļ | à¯į | à®ķà®³ | à¯į` (5 tokens)
- **Token Reduction:** 44.4%
- **Unicode Codepoints:** `U+0BAE U+0BB0 U+0B99 U+0BCD U+0B95 U+0BB3 U+0BCD`
- **Grapheme Clusters:** `ம | ர | ங் | க | ள்` (5 clusters)
- **Linguistic Analysis:** Pluralization with nasal assimilation sandhi: `மரம்` + `-கள்` $\\to$ `மரங்கள்`. Exp Candidate A captures `à®®à®°` (stem `மர`) and `à®ķà®³` (plural consonant sequence `கள`), preserving the morphological boundary.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_PLURAL_MERGE`.

#### OWN-REV-07: `பல்கலைக்கழகம்` (Nominal Compound)
- **Category:** `compound_words`
- **Candidate A:** `à® | ª | à®² | à¯į | à®ķ | à®² | à¯Ī | à®ķ | à¯į | à®ķ | à®´ | à®ķ | à®® | à¯į` (14 tokens)
- **Exp Candidate A:** `à®ª | à®² | à¯į | à®ķà®² | à¯Ī | à®ķ | à¯į | à®ķà®´ | à®ķà®® | à¯į` (10 tokens)
- **Token Reduction:** 28.6%
- **Unicode Codepoints:** `U+0BAA U+0BB2 U+0BCD U+0B95 U+0BB2 U+0BC8 U+0B95 U+0BCD U+0B95 U+0BB4 U+0B95 U+0BAE U+0BCD`
- **Grapheme Clusters:** `ப | ல் | க | லை | க் | க | ழ | க | ம்` (9 clusters)
- **Linguistic Analysis:** High-syllable compound: `பல` (many) + `கலை` (arts/science) + `கழகம்` (academy). Exp Candidate A groups internal syllables (`à®ķà®²` = `கல`, `à®ķà®´` = `கழ`, `à®ķà®®` = `கம`) without overmerging across the compound roots.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_SUBWORD_SPLIT`.

#### OWN-REV-08: `போறேன்` (Spoken Colloquial Contraction)
- **Category:** `spoken_vs_formal`
- **Candidate A:** `à® | ª | à¯ | ĭ | à®± | à¯ | ĩ | à®© | à¯į` (9 tokens)
- **Exp Candidate A:** `à®ª | à¯ĭ | à®± | à¯ĩ | à®© | à¯į` (6 tokens)
- **Token Reduction:** 33.3%
- **Unicode Codepoints:** `U+0BAA U+0BCB U+0BB1 U+0BC7 U+0BA9 U+0BCD`
- **Grapheme Clusters:** `போ | றே | ன்` (3 clusters)
- **Linguistic Analysis:** Spoken reduction of formal `போகிறேன்`. Exp Candidate A handles the colloquial stem without creating out-of-vocabulary artifacts.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_CONTRACTION`.

#### OWN-REV-09: `வீட்டிற்குள்` (Agglutinative Postposition)
- **Category:** `agglutinative_inflections`
- **Candidate A:** `à® | µ | à¯ | Ģ | à® | Ł | à¯į | à® | Ł | à®¿ | à®± | à¯į | à®ķ | à¯ģ | à® | ³ | à¯į` (17 tokens)
- **Exp Candidate A:** `à®µ | à¯Ģ | à®Ł | à¯į | à®Ł | à®¿ | à®± | à¯į | à®ķ | à¯ģ | à®³ | à¯į` (12 tokens)
- **Token Reduction:** 29.4%
- **Unicode Codepoints:** `U+0BB5 U+0BC0 U+0B9F U+0BCD U+0B9F U+0BBF U+0BB1 U+0BCD U+0B95 U+0BC1 U+0BB3 U+0BCD`
- **Grapheme Clusters:** `வீ | ட் | டி | ற் | கு | ள்` (6 clusters)
- **Linguistic Analysis:** Agglutinative stack: noun `வீடு` + oblique `ட்` + dative `இற்கு` + postposition `உள்`. Exp Candidate A eliminates 5 unnecessary orphan byte tokens.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_AGGLUTINATIVE_SPLIT`.

#### OWN-REV-10: `நாடுகளிலிருந்து` (Agglutinative Inflection Chain)
- **Category:** `agglutinative_inflections`
- **Candidate A:** `à® | ¨ | à®¾ | à® | Ł | à¯ģ | à®ķ | à® | ³ | à®¿ | à®² | à®¿ | à®° | à¯ģ | à® | ¨ | à¯į | à®¤ | à¯ģ` (19 tokens)
- **Exp Candidate A:** `à®¨ | à®¾ | à®Ł | à¯ģ | à®ķà®³ | à®¿ | à®² | à®¿ | à®° | à¯ģ | à®¨ | à¯į | à®¤ | à¯ģ` (14 tokens)
- **Token Reduction:** 26.3%
- **Unicode Codepoints:** `U+0BA8 U+0BBE U+0B9F U+0BC1 U+0B95 U+0BB3 U+0BBF U+0BB2 U+0BBF U+0BB0 U+0BC1 U+0BA8 U+0BCD U+0BA4 U+0BC1`
- **Grapheme Clusters:** `நா | டு | க | ளி | லி | ரு | ந் | து` (8 clusters)
- **Linguistic Analysis:** Multi-suffix chain: `நாடு` + `-கள்` + `-இல்` + `-இருந்து`. Exp Candidate A merges `à®ķà®³` (plural `-கள்`), keeping the grammatical chain well-structured.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_AGGLUTINATIVE_SPLIT`.

---

### SECTION B: ENGLISH PHENOMENA (OWN-REV-11 TO OWN-REV-20)

#### OWN-REV-11: `the` (Definite Article)
- **Category:** `common_words`
- **Candidate A:** `t | he` (2 tokens)
- **Exp Candidate A:** `t | he` (2 tokens)
- **Token Reduction:** 0.0%
- **Linguistic Analysis:** English high-frequency function word. Both tokenizers split `the` into `t` and `he` because it was not learned as an atomic merge in initial merges.
- **Owner Options:** `ACCEPT_MERGE; FLAG_OVERFRAGMENTED; ADD_ATOMIC_COMMON_WORD`.

#### OWN-REV-12: `microservice` (Closed Compound Technical Noun)
- **Category:** `technical_vocabulary`
- **Candidate A:** `m | i | c | r | o | s | e | r | v | i | c | e` (11 tokens)
- **Exp Candidate A:** `m | icroser | vice` (3 tokens)
- **Token Reduction:** 72.7%
- **CRITICAL OVERMERGE HAZARD (Audit Ref: OVM-AUD-01):** Exp Candidate A learned the token `icroser`, which crosses the compound boundary at offset 5 between prefix `micro-` and root `service`. In [TOKENIZER_OVERMERGING_AUDIT.csv](file:///C:/IGRIS/TOKENIZER_OVERMERGING_AUDIT.csv), this non-morphemic token also recurs in `microservices` (`m | icroser | vices`).
- **Owner Options:** `FLAG_NON_MORPHEMIC; REJECT_MERGE; RETRAIN_COMPOUND_SPLIT`.

#### OWN-REV-13: `asynchronous` (Computing Adjective)
- **Category:** `programming_terminology`
- **Candidate A:** `a | s | y | n | c | h | r | o | n | o | u | s` (12 tokens)
- **Exp Candidate A:** `as | ynchronous` (2 tokens)
- **Token Reduction:** 83.3%
- **CRITICAL OVERMERGE HAZARD (Audit Ref: OVM-AUD-05):** Exp Candidate A combines privative prefix `a-` with root onset `s-` into `as`, leaving `ynchronous`. This obscures the negation morpheme `a-`.
- **Owner Options:** `FLAG_NON_MORPHEMIC; REJECT_MERGE; APPROVE_STEM_SPLIT`.

#### OWN-REV-14: `middleware` (Technical Compound)
- **Category:** `programming_terminology`
- **Candidate A:** `m | i | d | d | l | e | w | a | r | e` (10 tokens)
- **Exp Candidate A:** `m | id | d | le | ware` (5 tokens)
- **Token Reduction:** 50.0%
- **Linguistic Analysis (Audit Ref: OVM-AUD-07):** Compound boundary between `middle` and `ware` (offset 6) is **CLEANLY PRESERVED**. Suffix `ware` is an intact atomic morpheme token. The root `middle` is fragmented into `m | id | d | le`.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_SUFFIX_ONLY`.

#### OWN-REV-15: `internationalization` (Multi-Affix Noun)
- **Category:** `long_words`
- **Candidate A:** 16 tokens
- **Exp Candidate A:** `in | tern | ational | ization` (4 tokens)
- **Token Reduction:** 75.0%
- **Linguistic Analysis (Audit Ref: OVM-AUD-10):** Suffixes `-ational` and `-ization` align cleanly with derivational morphemes. Subword `tern` spans the onset of `nation`.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_AFFIX_ALIGNMENT; BENEFICIAL_MERGE`.

#### OWN-REV-16: `unavoidable` (Prefixed/Suffixed Adjective)
- **Category:** `prefixes_and_suffixes`
- **Candidate A:** 10 tokens
- **Exp Candidate A:** `un | av | o | id | able` (5 tokens)
- **Token Reduction:** 50.0%
- **Linguistic Analysis (Audit Ref: OVM-AUD-12):** Negative prefix `un` and potential suffix `able` are preserved as exact atomic morpheme tokens. Root `avoid` is split into `av | o | id`.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_AFFIX_ALIGNMENT`.

#### OWN-REV-17: `API` (Capitalized Acronym)
- **Category:** `acronyms_initialisms`
- **Candidate A:** `A | P | I` (3 tokens)
- **Exp Candidate A:** `A | PI` (2 tokens)
- **Token Reduction:** 33.3%
- **Linguistic Analysis:** Exp Candidate A merges `PI` into a single subword.
- **Owner Options:** `ACCEPT_MERGE; PRESERVE_ACRONYM_SPLIT`.

#### OWN-REV-18: `user_id` (Snake_case Identifier)
- **Category:** `numbers_punctuation`
- **Candidate A:** `u | s | e | r | _ | id` (6 tokens)
- **Exp Candidate A:** `us | er | _ | id` (4 tokens)
- **Token Reduction:** 33.3%
- **Linguistic Analysis:** Exp Candidate A strictly isolates the underscore `_`, preserving code-syntax delimiters.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_DELIMITER_ISOLATION`.

#### OWN-REV-19: `parseToken()` (CamelCase Identifier + Syntax)
- **Category:** `numbers_punctuation`
- **Candidate A:** 11 tokens
- **Exp Candidate A:** `par | se | Token | ( | )` (5 tokens)
- **Token Reduction:** 54.5%
- **Linguistic Analysis:** Exp Candidate A merges `Token` into an intact subword and keeps parentheses `(` and `)` separate.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_CODE_SYNTAX`.

#### OWN-REV-20: `returns dict[str, Any]` (Code Type Signature)
- **Category:** `code_adjacent_text`
- **Candidate A:** 22 tokens
- **Exp Candidate A:** 15 tokens
- **Token Reduction:** 31.8%
- **Linguistic Analysis:** Exp Candidate A creates whitespace-prefixed subwords `Ġdict` and `ĠAny` while isolating brackets `[` and `]` and comma `,`.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_CODE_SYNTAX`.

---

### SECTION C: TANGLISH PHENOMENA (OWN-REV-21 TO OWN-REV-30)

#### OWN-REV-21: `server-ல்` (English Noun + Tamil Locative)
- **Category:** `english_with_tamil_suffixes`
- **Candidate A:** `s | e | r | v | e | r | - | à®² | à¯į` (7 tokens)
- **Exp Candidate A:** `ser | ver | - | à®² | à¯į` (5 tokens)
- **Token Reduction:** 28.6%
- **Linguistic Analysis:** Standard Tanglish technical code-mixing. Exp Candidate A reduces the English stem `server` to `ser | ver` and preserves the hyphen `-` and Tamil locative `-ல்` (`à®² | à¯į`) without cross-script bleeding.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_CODE_SWITCH_BOUNDARY; BENEFICIAL_MERGE`.

#### OWN-REV-22: `complex-ஆ` (English Adjective + Tamil Clitic)
- **Category:** `english_with_tamil_suffixes`
- **Candidate A:** 9 tokens
- **Exp Candidate A:** `com | ple | x | - | à®Ĩ` (5 tokens)
- **Token Reduction:** 44.4%
- **Linguistic Analysis:** Adverbial derivation with Tamil clitic `-ஆ`. Exp Candidate A cleanly separates the Latin stem `complex`, hyphen `-`, and Tamil clitic `ஆ`.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_CODE_SWITCH_BOUNDARY; BENEFICIAL_MERGE`.

#### OWN-REV-23: `testing-க்கு` (English Gerund + Tamil Dative)
- **Category:** `english_with_tamil_suffixes`
- **Candidate A:** 10 tokens
- **Exp Candidate A:** `t | est | ing | - | à®ķ | à¯į | à®ķ | à¯ģ` (8 tokens)
- **Token Reduction:** 20.0%
- **Linguistic Analysis:** Dative inflection on English gerund ("for testing"). English stem `testing` decomposes into natural morphemes `t | est | ing`, followed by clean hyphen and Tamil suffix.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_CODE_SWITCH_BOUNDARY`.

#### OWN-REV-24: `database-லிருந்து` (English Noun + Tamil Ablative)
- **Category:** `english_with_tamil_suffixes`
- **Candidate A:** 18 tokens
- **Exp Candidate A:** `d | at | abase | - | à®² | à®¿ | à®° | à¯ģ | à®¨ | à¯į | à®¤ | à¯ģ` (12 tokens)
- **Token Reduction:** 33.3%
- **Linguistic Analysis:** Ablative postposition ("from the database"). Exp Candidate A forms intact stem `abase` and isolates the Tamil case marker.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_CODE_SWITCH_BOUNDARY`.

#### OWN-REV-25: `deploy பண்ணினோம்` (English Verb + Tamil Light Verb)
- **Category:** `intra_sentential_code_switch`
- **Candidate A:** 18 tokens
- **Exp Candidate A:** `d | e | ploy | Ġà®ªà®£ | à¯į | à®£ | à®¿ | à®© | à¯ĭ | à®® | à¯į` (11 tokens)
- **Token Reduction:** 38.9%
- **Linguistic Analysis:** Light verb compound predicate: English `deploy` + Tamil `பண்ணினோம்` ("we deployed"). Exp Candidate A merges the onset `Ġபண` of the Tamil verb while strictly maintaining the space boundary.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_CODE_SWITCH_BOUNDARY`.

#### OWN-REV-26: `sprint planning முடிஞ்சிருச்சு` (English NP + Tamil Verb)
- **Category:** `intra_sentential_code_switch`
- **Candidate A:** 31 tokens
- **Exp Candidate A:** 20 tokens
- **Token Reduction:** 35.5%
- **Linguistic Analysis:** Multi-word intra-sentential switch. Exp Candidate A achieves 35.5% reduction without cross-word or cross-language boundary leakage.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_CODE_SWITCH_BOUNDARY`.

#### OWN-REV-27: `algorithm romba slow-ஆ இருக்கு` (Mixed 4-Way Code-Switch)
- **Category:** `intra_sentential_code_switch`
- **Candidate A:** 28 tokens
- **Exp Candidate A:** 15 tokens
- **Token Reduction:** 46.4%
- **Linguistic Analysis:** Four-way mixing: English technical + Romanized Tamil (`romba`) + hyphenated clitic (`slow-ஆ`) + Tamil verb (`இருக்கு`). Exp Candidate A merges Romanized `Ġromba` as a single token, proving synthetic Tanglish vocabulary capture.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_ROMANIZED_TAMIL_MERGE`.

#### OWN-REV-28: `Please check the logs da` (English + Tamil Discourse Particle)
- **Category:** `english_with_tamil_discourse_markers`
- **Candidate A:** 19 tokens
- **Exp Candidate A:** `Please | Ġcheck | Ġthe | Ġlogs | Ġda` (5 tokens)
- **Token Reduction:** 73.7%
- **Linguistic Analysis:** Colloquial pragmatic marker `da` appended to English sentence. Exp Candidate A achieves optimal 1 token per word across the entire sentence.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_DISCOURSE_PARTICLE; BENEFICIAL_MERGE`.

#### OWN-REV-29: `pannirukkom` (Romanized Tamil Informal Verb)
- **Category:** `spoken_informal_tanglish_verbs`
- **Candidate A:** `p | a | n | n | i | r | u | k | k | o | m` (10 tokens)
- **Exp Candidate A:** `p | ann | iru | k | k | om` (6 tokens)
- **Token Reduction:** 40.0%
- **Linguistic Analysis:** Romanized colloquial verb (`பண்ணியிருக்கிறோம்`). Exp Candidate A segments into meaningful morphemic chunks (`ann`, `iru`, `om`).
- **Owner Options:** `ACCEPT_MERGE; APPROVE_ROMANIZED_TAMIL_MERGE`.

#### OWN-REV-30: `கம்ப்யூட்டர்` (Tamil Loanword Transliteration)
- **Category:** `tamil_script_loanwords`
- **Candidate A:** 16 tokens
- **Exp Candidate A:** `à®ķà®® | à¯į | à®ª | à¯į | à®¯ | à¯Ĥ | à®Ł | à¯į | à®Łà®° | à¯į` (10 tokens)
- **Token Reduction:** 37.5%
- **Linguistic Analysis:** Transliteration of English "computer". Exp Candidate A merges initial syllable `கம்` and terminal syllable `டர்`.
- **Owner Options:** `ACCEPT_MERGE; APPROVE_LOANWORD_MERGE`.

---

## 4. Summary Guidance & Epistemic Matrix for the Sole Developer Owner

```
+───────────────────────────────────────────────────────────────────────────────────────────────+
|                                    EPISTEMIC FINDINGS MATRIX                                  |
+───────────────────────────────+───────────────────────────────+───────────────────────────────+
| Category                      | Finding / Metric              | Status / Classification       |
+───────────────────────────────+───────────────────────────────+───────────────────────────────+
| Decoding Correctness          | 100.0% Round-trip fidelity    | VERIFIED FACT (Bit-for-bit)   |
| ByteLevel Display Mapping     | GPT-2 bijective mapping       | VERIFIED FACT                 |
| Pipeline Normalization        | normalizer is null in config  | VERIFIED FACT                 |
| NFC vs NFD Divergence         | Only affects 'கௌ' in Tamil   | VERIFIED FACT                 |
| English Compound Overmerge    | microservice -> icroser       | VERIFIED FACT (Critical)      |
| Compound Boundary Ware        | middleware -> ware intact     | VERIFIED FACT (Clean boundary)|
| Code-Switch Boundary Clean    | Zero script leakage           | VERIFIED FACT                 |
| Pulli Reasoning Impact        | Detached pulli improves lm    | UNSUPPORTED HYPOTHESIS        |
| Per-token UTF-8 Superiority   | Tokens must be valid UTF-8    | UNSUPPORTED HYPOTHESIS        |
| Compression = Quality         | Lower fertility = better      | UNSUPPORTED HYPOTHESIS        |
+───────────────────────────────+───────────────────────────────+───────────────────────────────+
```

### Actionable Next Steps:
1. **Evaluate Overmerges:** Consider rejecting `OWN-REV-12` (`microservice`) and `OWN-REV-13` (`asynchronous`) due to non-morphemic stem merging.
2. **Affix Approval:** Approve cleanly aligned morphemic merges in Tamil (`-தல்`, `-கள்`, `-லிருந்து`) and English (`-ational`, `-ization`, `un-`, `-able`).
3. **Record Determinations:** When ready, update `human_review_decision` and `reviewer_rationale` in [TOKENIZER_OWNER_REVIEW_30.csv](file:///C:/IGRIS/TOKENIZER_OWNER_REVIEW_30.csv).
"""

guide_path = WORKSPACE_ROOT / "TOKENIZER_OWNER_REVIEW_GUIDE.md"
with open(guide_path, "w", encoding="utf-8") as f:
    f.write(guide_content)

shutil.copy2(guide_path, PATCH_ROOT / "TOKENIZER_OWNER_REVIEW_GUIDE.md")
shutil.copy2(guide_path, ARTIFACT_DIR / "TOKENIZER_OWNER_REVIEW_GUIDE.md")

print(f"Updated and mirrored {guide_path}.")
