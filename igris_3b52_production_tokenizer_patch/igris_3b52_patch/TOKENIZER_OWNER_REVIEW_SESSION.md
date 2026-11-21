# IGRIS Tokenizer Owner Review Session: 30 Prioritized Cases

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

### OWN-REV-01: `க்` (pulli_and_virama)
- **Technical Concern Summary:** Detached pulli diacritic consumes 2 token sequence positions per pure consonant.
- **Original Input Text:** `க்`
- **Original Candidate A Tokenization:** `à®ķ | à¯į`
- **Experimental Candidate A Tokenization:** `à®ķ | à¯į`
- **Token IDs:**
  - Candidate A: `[277, 271]`
  - Exp Candidate A: `[272, 270]`
- **Token Counts:** Candidate A = 2 tokens | Exp Candidate A = 2 tokens (Reduction: 0.0%)
- **Unicode Codepoints:** `U+0B95 U+0BCD`
- **Grapheme-Boundary Observations:** 1 grapheme cluster (க்); 2 codepoints. Both tokenizers cut between base consonant and combining pulli (1 character cut inside grapheme).
- **Morphological Observations:** Pure consonant formed by inherent vowel cancellation.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Pulli remains a detached diacritic token (à¯į). Downstream impact on attention and reasoning remains an unverified hypothesis.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-02: `கௌ` (uyirmei_combinations)
- **Technical Concern Summary:** Two-token diphthong segmentation; sensitive to upstream NFC vs NFD normalization.
- **Original Input Text:** `கௌ`
- **Original Candidate A Tokenization:** `à®ķ | à¯ | Į`
- **Experimental Candidate A Tokenization:** `à®ķ | à¯Į`
- **Token IDs:**
  - Candidate A: `[277, 270, 246]`
  - Exp Candidate A: `[272, 1147]`
- **Token Counts:** Candidate A = 3 tokens | Exp Candidate A = 2 tokens (Reduction: 33.3%)
- **Unicode Codepoints:** `U+0B95 U+0BCC`
- **Grapheme-Boundary Observations:** 1 grapheme cluster (கௌ). Exp A isolates base consonant into à®ķ and au-sign into à¯Į (1 character cut inside grapheme).
- **Morphological Observations:** Diphthongal uyirmei syllable /kau/.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Pipeline normalizer is null. If text arrives in NFD form, token count increases from 2 to 4.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-03: `ஸ்ரீ` (grantha_and_conjuncts)
- **Technical Concern Summary:** Multi-codepoint Grantha ligature fragmented across 4 tokens in Exp A (6 in Cand A).
- **Original Input Text:** `ஸ்ரீ`
- **Original Candidate A Tokenization:** `à® | ¸ | à¯į | à®° | à¯ | Ģ`
- **Experimental Candidate A Tokenization:** `à®¸ | à¯į | à®° | à¯Ģ`
- **Token IDs:**
  - Candidate A: `[268, 128, 271, 286, 270, 234]`
  - Exp Candidate A: `[964, 270, 284, 390]`
- **Token Counts:** Candidate A = 6 tokens | Exp Candidate A = 4 tokens (Reduction: 33.3%)
- **Unicode Codepoints:** `U+0BB8 U+0BCD U+0BB0 U+0BC0`
- **Grapheme-Boundary Observations:** 2 grapheme clusters (ஸ், ரீ); 4 codepoints. Neither tokenizer treats Sri as an atomic token; both cut between base consonants and marks.
- **Morphological Observations:** Traditional Grantha honorific ligature Sri.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Candidate A fragments into 6 tokens with incomplete bytes; Exp A forms 4 complete-character tokens but lacks an atomic ligature merge.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-04: `செய்தல்` (roots_and_suffixes)
- **Technical Concern Summary:** Beneficial inflectional compression (33.3%), but retains detached pulli on terminal consonant.
- **Original Input Text:** `செய்தல்`
- **Original Candidate A Tokenization:** `à® | ļ | à¯ | Ĩ | à®¯ | à¯į | à®¤ | à®² | à¯į`
- **Experimental Candidate A Tokenization:** `à®ļ | à¯Ĩ | à®¯ | à¯į | à®¤à®² | à¯į`
- **Token IDs:**
  - Candidate A: `[268, 260, 270, 240, 312, 271, 282, 294, 271]`
  - Exp Candidate A: `[317, 325, 283, 270, 652, 270]`
- **Token Counts:** Candidate A = 9 tokens | Exp Candidate A = 6 tokens (Reduction: 33.3%)
- **Unicode Codepoints:** `U+0B9A U+0BC6 U+0BAF U+0BCD U+0BA4 U+0BB2 U+0BCD`
- **Grapheme-Boundary Observations:** 4 grapheme clusters (செ, ய், த, ல்); 7 codepoints. Cuts inside graphemes ಸೆ and ய் occur in both.
- **Morphological Observations:** Clear morphological boundary between verbal stem செய் and nominalizing suffix -தல்.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Exp A merges stem coda of suffix into 'à®¤à®²'. Does not overmerge across verb root.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-05: `வந்தேன்` (tense_and_person)
- **Technical Concern Summary:** 7 tokens for a single 4-syllable finite verb; compression is modest.
- **Original Input Text:** `வந்தேன்`
- **Original Candidate A Tokenization:** `à® | µ | à® | ¨ | à¯į | à®¤ | à¯ | ĩ | à®© | à¯į`
- **Experimental Candidate A Tokenization:** `à®µ | à®¨ | à¯į | à®¤ | à¯ĩ | à®© | à¯į`
- **Token IDs:**
  - Candidate A: `[268, 125, 268, 113, 271, 282, 270, 241, 285, 271]`
  - Exp Candidate A: `[300, 362, 270, 275, 351, 279, 270]`
- **Token Counts:** Candidate A = 10 tokens | Exp Candidate A = 7 tokens (Reduction: 30.0%)
- **Unicode Codepoints:** `U+0BB5 U+0BA8 U+0BCD U+0BA4 U+0BC7 U+0BA9 U+0BCD`
- **Grapheme-Boundary Observations:** 4 grapheme clusters (வ, ந், தே, ன்); 7 codepoints. Combining marks cut internally.
- **Morphological Observations:** Finite past verb; clear inflectional boundary between stem and pronominal agreement.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Exp A reduces from 10 to 7 tokens. Grammatical agreement suffix remains identifiable.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-06: `மரங்கள்` (singular_and_plural)
- **Technical Concern Summary:** Plural marker is preserved cleanly, but terminal pulli remains detached.
- **Original Input Text:** `மரங்கள்`
- **Original Candidate A Tokenization:** `à®® | à®° | à® | Ļ | à¯į | à®ķ | à® | ³ | à¯į`
- **Experimental Candidate A Tokenization:** `à®®à®° | à®Ļ | à¯į | à®ķà®³ | à¯į`
- **Token IDs:**
  - Candidate A: `[278, 286, 268, 259, 271, 277, 268, 123, 271]`
  - Exp Candidate A: `[609, 355, 270, 309, 270]`
- **Token Counts:** Candidate A = 9 tokens | Exp Candidate A = 5 tokens (Reduction: 44.4%)
- **Unicode Codepoints:** `U+0BAE U+0BB0 U+0B99 U+0BCD U+0B95 U+0BB3 U+0BCD`
- **Grapheme-Boundary Observations:** 5 grapheme clusters (ம, ர, ங், க, ள்); 7 codepoints.
- **Morphological Observations:** Plural inflection with external sandhi coda mutation /m/ -> /ŋ/.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Exp A groups stem 'மர' and plural consonants 'கள'. Plural marker is preserved cleanly.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-07: `பல்கலைக்கழகம்` (compound_words)
- **Technical Concern Summary:** 10 tokens in Exp A (down from 14); subwords are sub-syllabic rather than full root stems.
- **Original Input Text:** `பல்கலைக்கழகம்`
- **Original Candidate A Tokenization:** `à® | ª | à®² | à¯į | à®ķ | à®² | à¯Ī | à®ķ | à¯į | à®ķ | à®´ | à®ķ | à®® | à¯į`
- **Experimental Candidate A Tokenization:** `à®ª | à®² | à¯į | à®ķà®² | à¯Ī | à®ķ | à¯į | à®ķà®´ | à®ķà®® | à¯į`
- **Token IDs:**
  - Candidate A: `[268, 115, 294, 271, 277, 294, 317, 277, 271, 277, 283, 277, 278, 271]`
  - Exp Candidate A: `[276, 288, 270, 849, 285, 272, 270, 1151, 967, 270]`
- **Token Counts:** Candidate A = 14 tokens | Exp Candidate A = 10 tokens (Reduction: 28.6%)
- **Unicode Codepoints:** `U+0BAA U+0BB2 U+0BCD U+0B95 U+0BB2 U+0BC8 U+0B95 U+0BCD U+0B95 U+0BB4 U+0B95 U+0BAE U+0BCD`
- **Grapheme-Boundary Observations:** 9 grapheme clusters; 13 codepoints.
- **Morphological Observations:** Three-constituent nominal compound with sandhi gemination.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Exp A groups sub-syllabic pairs (கல, கழ, கம) without crossing primary compound boundaries.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-08: `போறேன்` (spoken_vs_formal)
- **Technical Concern Summary:** Spoken variant consumes 6 tokens; reflects lack of colloquial spoken data in merge training.
- **Original Input Text:** `போறேன்`
- **Original Candidate A Tokenization:** `à® | ª | à¯ | ĭ | à®± | à¯ | ĩ | à®© | à¯į`
- **Experimental Candidate A Tokenization:** `à®ª | à¯ĭ | à®± | à¯ĩ | à®© | à¯į`
- **Token IDs:**
  - Candidate A: `[268, 115, 270, 245, 287, 270, 241, 285, 271]`
  - Exp Candidate A: `[276, 356, 277, 351, 279, 270]`
- **Token Counts:** Candidate A = 9 tokens | Exp Candidate A = 6 tokens (Reduction: 33.3%)
- **Unicode Codepoints:** `U+0BAA U+0BCB U+0BB1 U+0BC7 U+0BA9 U+0BCD`
- **Grapheme-Boundary Observations:** 3 grapheme clusters (போ, றே, ன்); 6 codepoints.
- **Morphological Observations:** Colloquial spoken contraction of formal போகிறேன்.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Colloquial spoken contraction is preserved without producing out-of-vocabulary fallback bytes.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-09: `வீட்டிற்குள்` (agglutinative_inflections)
- **Technical Concern Summary:** High sequence fertility (12 tokens for 1 word); agglutinative suffixes remain heavily segmented.
- **Original Input Text:** `வீட்டிற்குள்`
- **Original Candidate A Tokenization:** `à® | µ | à¯ | Ģ | à® | Ł | à¯į | à® | Ł | à®¿ | à®± | à¯į | à®ķ | à¯ģ | à® | ³ | à¯į`
- **Experimental Candidate A Tokenization:** `à®µ | à¯Ģ | à®Ł | à¯į | à®Ł | à®¿ | à®± | à¯į | à®ķ | à¯ģ | à®³ | à¯į`
- **Token IDs:**
  - Candidate A: `[268, 125, 270, 234, 268, 265, 271, 268, 265, 272, 287, 271, 277, 288, 268, 123, 271]`
  - Exp Candidate A: `[300, 390, 278, 270, 278, 274, 277, 270, 272, 273, 291, 270]`
- **Token Counts:** Candidate A = 17 tokens | Exp Candidate A = 12 tokens (Reduction: 29.4%)
- **Unicode Codepoints:** `U+0BB5 U+0BC0 U+0B9F U+0BCD U+0B9F U+0BBF U+0BB1 U+0BCD U+0B95 U+0BC1 U+0BB3 U+0BCD`
- **Grapheme-Boundary Observations:** 6 grapheme clusters; 12 codepoints. All combining marks detached.
- **Morphological Observations:** Agglutinative postpositional stack: noun + oblique + dative + locative.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Exp A reduces from 17 to 12 tokens. Agglutinative suffix chain remains split across morphemes.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-10: `நாடுகளிலிருந்து` (agglutinative_inflections)
- **Technical Concern Summary:** 14 tokens in Exp A (down from 19); represents high sequence overhead for agglutinative inflections.
- **Original Input Text:** `நாடுகளிலிருந்து`
- **Original Candidate A Tokenization:** `à® | ¨ | à®¾ | à® | Ł | à¯ģ | à®ķ | à® | ³ | à®¿ | à®² | à®¿ | à®° | à¯ģ | à® | ¨ | à¯į | à®¤ | à¯ģ`
- **Experimental Candidate A Tokenization:** `à®¨ | à®¾ | à®Ł | à¯ģ | à®ķà®³ | à®¿ | à®² | à®¿ | à®° | à¯ģ | à®¨ | à¯į | à®¤ | à¯ģ`
- **Token IDs:**
  - Candidate A: `[268, 113, 313, 268, 265, 288, 277, 268, 123, 272, 294, 272, 286, 288, 268, 113, 271, 282, 288]`
  - Exp Candidate A: `[362, 281, 278, 273, 309, 274, 288, 274, 284, 273, 362, 270, 275, 273]`
- **Token Counts:** Candidate A = 19 tokens | Exp Candidate A = 14 tokens (Reduction: 26.3%)
- **Unicode Codepoints:** `U+0BA8 U+0BBE U+0B9F U+0BC1 U+0B95 U+0BB3 U+0BBF U+0BB2 U+0BBF U+0BB0 U+0BC1 U+0BA8 U+0BCD U+0BA4 U+0BC1`
- **Grapheme-Boundary Observations:** 8 grapheme clusters; 15 codepoints.
- **Morphological Observations:** Multi-morpheme agglutinative case stack ('from countries').
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Exp A isolates plural marker -கள் and ablative -இருந்து into distinct subword groups.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

## 3. Review Section B: English Language Phenomena (10 Cases)

### OWN-REV-11: `the` (common_words)
- **Technical Concern Summary:** Highest-frequency English word split into 2 tokens across both tokenizers.
- **Original Input Text:** `the`
- **Original Candidate A Tokenization:** `t | he`
- **Experimental Candidate A Tokenization:** `t | he`
- **Token IDs:**
  - Candidate A: `[95, 291]`
  - Exp Candidate A: `[95, 326]`
- **Token Counts:** Candidate A = 2 tokens | Exp Candidate A = 2 tokens (Reduction: 0.0%)
- **Unicode Codepoints:** `U+0074 U+0068 U+0065`
- **Grapheme-Boundary Observations:** 3 grapheme clusters (t, h, e); single-byte ASCII. 0 cuts inside graphemes.
- **Morphological Observations:** Monomorphemic English closed-class grammatical functional head.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Both Candidate A and Exp A segment 'the' into 2 tokens ('t | he') because 'the' was not learned as an atomic merge in initial passes.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-12: `microservice` (technical_vocabulary)
- **Technical Concern Summary:** CRITICAL OVERMERGE: Subword 'icroser' straddles prefix-stem boundary, harming compositional semantics.
- **Original Input Text:** `microservice`
- **Original Candidate A Tokenization:** `m | i | c | r | o | s | er | v | i | c | e`
- **Experimental Candidate A Tokenization:** `m | icroser | vice`
- **Token IDs:**
  - Candidate A: `[88, 84, 78, 93, 90, 94, 284, 97, 84, 78, 80]`
  - Exp Candidate A: `[88, 929, 738]`
- **Token Counts:** Candidate A = 11 tokens | Exp Candidate A = 3 tokens (Reduction: 72.7%)
- **Unicode Codepoints:** `U+006D U+0069 U+0063 U+0072 U+006F U+0073 U+0065 U+0072 U+0076 U+0069 U+0063 U+0065`
- **Grapheme-Boundary Observations:** 12 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.
- **Morphological Observations:** CROSSES_MORPHEME_BOUNDARY: Closed technical compound. Boundary between micro- and service is severed.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Exp A learned the non-morphemic subword 'icroser' spanning across the boundary (offset 5). Recurs in 'microservices'.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-13: `asynchronous` (programming_terminology)
- **Technical Concern Summary:** CRITICAL OVERMERGE: Obscures privative negation prefix 'a-' into unrelated subword 'as'.
- **Original Input Text:** `asynchronous`
- **Original Candidate A Tokenization:** `a | s | y | n | c | h | r | o | n | o | u | s`
- **Experimental Candidate A Tokenization:** `as | ynchronous`
- **Token IDs:**
  - Candidate A: `[76, 94, 100, 89, 78, 83, 93, 90, 89, 90, 96, 94]`
  - Exp Candidate A: `[352, 1956]`
- **Token Counts:** Candidate A = 12 tokens | Exp Candidate A = 2 tokens (Reduction: 83.3%)
- **Unicode Codepoints:** `U+0061 U+0073 U+0079 U+006E U+0063 U+0068 U+0072 U+006F U+006E U+006F U+0075 U+0073`
- **Grapheme-Boundary Observations:** 12 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.
- **Morphological Observations:** CROSSES_MORPHEME_BOUNDARY: Greek negation prefix a- merged with root onset s-.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Exp A collapses into 'as | ynchronous', obscuring the privative negation prefix and mimicking function word 'as'.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-14: `middleware` (programming_terminology)
- **Technical Concern Summary:** Compound boundary is preserved, but base root 'middle' is fragmented into 'm | id | d | le'.
- **Original Input Text:** `middleware`
- **Original Candidate A Tokenization:** `m | i | d | d | l | e | w | a | r | e`
- **Experimental Candidate A Tokenization:** `m | id | d | le | ware`
- **Token IDs:**
  - Candidate A: `[88, 84, 79, 79, 87, 80, 98, 76, 93, 80]`
  - Exp Candidate A: `[88, 380, 79, 316, 607]`
- **Token Counts:** Candidate A = 10 tokens | Exp Candidate A = 5 tokens (Reduction: 50.0%)
- **Unicode Codepoints:** `U+006D U+0069 U+0064 U+0064 U+006C U+0065 U+0077 U+0061 U+0072 U+0065`
- **Grapheme-Boundary Observations:** 10 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.
- **Morphological Observations:** CLEAR_MORPHEME_BOUNDARY: Compound boundary between middle and ware is cleanly preserved.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Suffix 'ware' is an intact atomic token. Root 'middle' is fragmented internally into 4 pieces.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-15: `internationalization` (long_words)
- **Technical Concern Summary:** Subword 'tern' slightly straddles prefix-root boundary, but derivational affixes align cleanly.
- **Original Input Text:** `internationalization`
- **Original Candidate A Tokenization:** `in | t | er | na | t | i | o | n | al | i | z | a | t | i | o | n`
- **Experimental Candidate A Tokenization:** `in | tern | ational | ization`
- **Token IDs:**
  - Candidate A: `[301, 95, 284, 303, 95, 84, 90, 89, 297, 84, 101, 76, 95, 84, 90, 89]`
  - Exp Candidate A: `[280, 1284, 1638, 535]`
- **Token Counts:** Candidate A = 16 tokens | Exp Candidate A = 4 tokens (Reduction: 75.0%)
- **Unicode Codepoints:** `U+0069 U+006E U+0074 U+0065 U+0072 U+006E U+0061 U+0074 U+0069 U+006F U+006E U+0061 U+006C U+0069 U+007A U+0061 U+0074 U+0069 U+006F U+006E`
- **Grapheme-Boundary Observations:** 20 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.
- **Morphological Observations:** POTENTIAL_OVERMERGE: Suffixes -ational and -ization are cleanly aligned, but 'tern' spans prefix-root juncture.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Exp A achieves 75% compression (4 tokens vs 16). Suffix boundaries align well with derivational morphology.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-16: `unavoidable` (prefixes_and_suffixes)
- **Technical Concern Summary:** Clean affix preservation ('un' and 'able'), but root 'avoid' is fragmented.
- **Original Input Text:** `unavoidable`
- **Original Candidate A Tokenization:** `u | na | v | o | i | d | a | b | l | e`
- **Experimental Candidate A Tokenization:** `un | av | o | id | able`
- **Token IDs:**
  - Candidate A: `[96, 303, 97, 90, 84, 79, 76, 77, 87, 80]`
  - Exp Candidate A: `[384, 685, 90, 380, 512]`
- **Token Counts:** Candidate A = 10 tokens | Exp Candidate A = 5 tokens (Reduction: 50.0%)
- **Unicode Codepoints:** `U+0075 U+006E U+0061 U+0076 U+006F U+0069 U+0064 U+0061 U+0062 U+006C U+0065`
- **Grapheme-Boundary Observations:** 11 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.
- **Morphological Observations:** CLEAR_MORPHEME_BOUNDARY: Both prefix un- and suffix -able are preserved as exact atomic morpheme tokens.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Base root 'avoid' is fragmented into 'av | o | id', but affix boundaries are strictly maintained.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-17: `API` (acronyms_initialisms)
- **Technical Concern Summary:** Exp A creates 2-letter uppercase merge 'PI'; initialism is not fully atomic.
- **Original Input Text:** `API`
- **Original Candidate A Tokenization:** `A | P | I`
- **Experimental Candidate A Tokenization:** `A | PI`
- **Token IDs:**
  - Candidate A: `[44, 59, 52]`
  - Exp Candidate A: `[44, 1424]`
- **Token Counts:** Candidate A = 3 tokens | Exp Candidate A = 2 tokens (Reduction: 33.3%)
- **Unicode Codepoints:** `U+0041 U+0050 U+0049`
- **Grapheme-Boundary Observations:** 3 grapheme clusters (A, P, I); single-byte ASCII. 0 cuts inside graphemes.
- **Morphological Observations:** All-caps technical initialism: Application Programming Interface.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Cand A segments as 3 single-letter tokens ('A | P | I'); Exp A merges 'PI' ('A | PI').
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-18: `user_id` (numbers_punctuation)
- **Technical Concern Summary:** Stem 'user' is split into 'us | er', but delimiter boundary is clean.
- **Original Input Text:** `user_id`
- **Original Candidate A Tokenization:** `u | s | er | _ | i | d`
- **Experimental Candidate A Tokenization:** `us | er | _ | id`
- **Token IDs:**
  - Candidate A: `[96, 94, 284, 74, 84, 79]`
  - Exp Candidate A: `[363, 286, 74, 380]`
- **Token Counts:** Candidate A = 6 tokens | Exp Candidate A = 4 tokens (Reduction: 33.3%)
- **Unicode Codepoints:** `U+0075 U+0073 U+0065 U+0072 U+005F U+0069 U+0064`
- **Grapheme-Boundary Observations:** 7 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.
- **Morphological Observations:** CLEAR_MORPHEME_BOUNDARY: Underscore delimiter is strictly isolated as an independent token.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Underscore is not merged into alphanumeric tokens, preserving syntax boundaries in programming text.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-19: `parseToken()` (numbers_punctuation)
- **Technical Concern Summary:** Stem 'parse' is split as 'par | se', but CamelCase identifier boundary is respected.
- **Original Input Text:** `parseToken()`
- **Original Candidate A Tokenization:** `p | a | r | s | e | T | o | k | en | ( | )`
- **Experimental Candidate A Tokenization:** `par | se | Token | ( | )`
- **Token IDs:**
  - Candidate A: `[91, 76, 93, 94, 80, 63, 90, 86, 299, 19, 20]`
  - Exp Candidate A: `[1131, 1136, 1969, 19, 20]`
- **Token Counts:** Candidate A = 11 tokens | Exp Candidate A = 5 tokens (Reduction: 54.5%)
- **Unicode Codepoints:** `U+0070 U+0061 U+0072 U+0073 U+0065 U+0054 U+006F U+006B U+0065 U+006E U+0028 U+0029`
- **Grapheme-Boundary Observations:** 12 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.
- **Morphological Observations:** CLEAR_MORPHEME_BOUNDARY: Method identifier and syntactic parentheses isolated cleanly.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Exp A merges capitalized 'Token' and isolates '(' and ')', reducing tokens from 11 to 5.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-20: `returns dict[str, Any]` (code_adjacent_text)
- **Technical Concern Summary:** Type signature tokenization is clean; punctuation delimiters are isolated.
- **Original Input Text:** `returns dict[str, Any]`
- **Original Candidate A Tokenization:** `r | e | t | u | r | n | s | Ġ | d | i | c | t | [ | s | t | r | , | Ġ | A | n | y | ]`
- **Experimental Candidate A Tokenization:** `re | t | urn | s | Ġd | ic | t | [ | st | r | , | ĠA | n | y | ]`
- **Token IDs:**
  - Candidate A: `[93, 80, 95, 96, 93, 89, 94, 232, 79, 84, 78, 95, 70, 94, 95, 93, 23, 232, 44, 89, 100, 72]`
  - Exp Candidate A: `[292, 95, 1694, 94, 306, 312, 95, 70, 412, 93, 23, 1140, 89, 100, 72]`
- **Token Counts:** Candidate A = 22 tokens | Exp Candidate A = 15 tokens (Reduction: 31.8%)
- **Unicode Codepoints:** `U+0072 U+0065 U+0074 U+0075 U+0072 U+006E U+0073 U+0020 U+0064 U+0069 U+0063 U+0074 U+005B U+0073 U+0074 U+0072 U+002C U+0020 U+0041 U+006E U+0079 U+005D`
- **Grapheme-Boundary Observations:** 22 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.
- **Morphological Observations:** CLEAR_MORPHEME_BOUNDARY: Code type annotation with delimiters and generics brackets.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Exp A forms leading-space tokens 'Ġdict' and 'ĠAny' while isolating brackets and commas.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

## 4. Review Section C: Tanglish Language Phenomena (10 Cases)

### OWN-REV-21: `server-ல்` (english_with_tamil_suffixes)
- **Technical Concern Summary:** Tamil locative suffix is cleanly isolated, but pulli remains detached.
- **Original Input Text:** `server-ல்`
- **Original Candidate A Tokenization:** `s | er | v | er | - | à®² | à¯į`
- **Experimental Candidate A Tokenization:** `ser | ver | - | à®² | à¯į`
- **Token IDs:**
  - Candidate A: `[94, 284, 97, 284, 24, 294, 271]`
  - Exp Candidate A: `[643, 453, 24, 288, 270]`
- **Token Counts:** Candidate A = 7 tokens | Exp Candidate A = 5 tokens (Reduction: 28.6%)
- **Unicode Codepoints:** `U+0073 U+0065 U+0072 U+0076 U+0065 U+0072 U+002D U+0BB2 U+0BCD`
- **Grapheme-Boundary Observations:** 8 grapheme clusters; 9 codepoints. Pulli on ல் detached in both.
- **Morphological Observations:** CLEAR_MORPHEME_BOUNDARY: English root and Tamil locative suffix partitioned by hyphen delimiter.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Zero cross-script bleeding. Hyphen acts as an impermeable barrier.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-22: `complex-ஆ` (english_with_tamil_suffixes)
- **Technical Concern Summary:** Exp A resolves Candidate A's byte-level splitting of clitic 'ஆ'.
- **Original Input Text:** `complex-ஆ`
- **Original Candidate A Tokenization:** `c | o | m | p | l | ex | - | à® | Ĩ`
- **Experimental Candidate A Tokenization:** `com | ple | x | - | à®Ĩ`
- **Token IDs:**
  - Candidate A: `[78, 90, 88, 91, 87, 300, 24, 268, 240]`
  - Exp Candidate A: `[472, 571, 99, 24, 766]`
- **Token Counts:** Candidate A = 9 tokens | Exp Candidate A = 5 tokens (Reduction: 44.4%)
- **Unicode Codepoints:** `U+0063 U+006F U+006D U+0070 U+006C U+0065 U+0078 U+002D U+0B86`
- **Grapheme-Boundary Observations:** 9 grapheme clusters; 9 codepoints. Exp A has 0 character cuts and 0 byte cuts inside ஆ.
- **Morphological Observations:** CLEAR_MORPHEME_BOUNDARY: Latin stem and Tamil clitic partitioned cleanly.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Cand A splits ஆ at byte offset 10 into incomplete bytes; Exp A preserves entire 3-byte token à®Ĩ.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-23: `testing-க்கு` (english_with_tamil_suffixes)
- **Technical Concern Summary:** Tamil dative suffix requires 4 tokens; Latin stem achieves morphemic alignment.
- **Original Input Text:** `testing-க்கு`
- **Original Candidate A Tokenization:** `t | es | t | in | g | - | à®ķ | à¯į | à®ķ | à¯ģ`
- **Experimental Candidate A Tokenization:** `t | est | ing | - | à®ķ | à¯į | à®ķ | à¯ģ`
- **Token IDs:**
  - Candidate A: `[95, 281, 95, 301, 82, 24, 277, 271, 277, 288]`
  - Exp Candidate A: `[95, 398, 307, 24, 272, 270, 272, 273]`
- **Token Counts:** Candidate A = 10 tokens | Exp Candidate A = 8 tokens (Reduction: 20.0%)
- **Unicode Codepoints:** `U+0074 U+0065 U+0073 U+0074 U+0069 U+006E U+0067 U+002D U+0B95 U+0BCD U+0B95 U+0BC1`
- **Grapheme-Boundary Observations:** 10 grapheme clusters; 12 codepoints. Dative suffix has internal combining mark cuts.
- **Morphological Observations:** CLEAR_MORPHEME_BOUNDARY: Latin gerund base and Tamil dative suffix partitioned by hyphen.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Latin stem 'testing' decomposes into natural morphemes 't | est | ing'; suffix -க்கு is isolated.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-24: `database-லிருந்து` (english_with_tamil_suffixes)
- **Technical Concern Summary:** Ablative suffix chain consumes 8 tokens; no script leakage observed.
- **Original Input Text:** `database-லிருந்து`
- **Original Candidate A Tokenization:** `d | a | t | a | b | a | s | e | - | à®² | à®¿ | à®° | à¯ģ | à® | ¨ | à¯į | à®¤ | à¯ģ`
- **Experimental Candidate A Tokenization:** `d | at | abase | - | à®² | à®¿ | à®° | à¯ģ | à®¨ | à¯į | à®¤ | à¯ģ`
- **Token IDs:**
  - Candidate A: `[79, 76, 95, 76, 77, 76, 94, 80, 24, 294, 272, 286, 288, 268, 113, 271, 282, 288]`
  - Exp Candidate A: `[79, 293, 562, 24, 288, 274, 284, 273, 362, 270, 275, 273]`
- **Token Counts:** Candidate A = 18 tokens | Exp Candidate A = 12 tokens (Reduction: 33.3%)
- **Unicode Codepoints:** `U+0064 U+0061 U+0074 U+0061 U+0062 U+0061 U+0073 U+0065 U+002D U+0BB2 U+0BBF U+0BB0 U+0BC1 U+0BA8 U+0BCD U+0BA4 U+0BC1`
- **Grapheme-Boundary Observations:** 13 grapheme clusters; 17 codepoints.
- **Morphological Observations:** CLEAR_MORPHEME_BOUNDARY: Multi-suffix ablative case cleanly partitioned from Latin stem.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Exp A reduces from 18 to 12 tokens. Latin base 'database' forms stem 'abase'.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-25: `deploy பண்ணினோம்` (intra_sentential_code_switch)
- **Technical Concern Summary:** Clean code-switching boundary; 11 tokens in Exp A (down from 18 in Cand A).
- **Original Input Text:** `deploy பண்ணினோம்`
- **Original Candidate A Tokenization:** `d | e | p | lo | y | Ġà® | ª | à® | £ | à¯į | à® | £ | à®¿ | à®© | à¯ | ĭ | à®® | à¯į`
- **Experimental Candidate A Tokenization:** `d | e | ploy | Ġà®ªà®£ | à¯į | à®£ | à®¿ | à®© | à¯ĭ | à®® | à¯į`
- **Token IDs:**
  - Candidate A: `[79, 80, 91, 302, 100, 273, 115, 268, 108, 271, 268, 108, 272, 285, 270, 245, 278, 271]`
  - Exp Candidate A: `[79, 80, 628, 336, 270, 294, 274, 279, 356, 282, 270]`
- **Token Counts:** Candidate A = 18 tokens | Exp Candidate A = 11 tokens (Reduction: 38.9%)
- **Unicode Codepoints:** `U+0064 U+0065 U+0070 U+006C U+006F U+0079 U+0020 U+0BAA U+0BA3 U+0BCD U+0BA3 U+0BBF U+0BA9 U+0BCB U+0BAE U+0BCD`
- **Grapheme-Boundary Observations:** 12 grapheme clusters; 15 codepoints.
- **Morphological Observations:** CLEAR_MORPHEME_BOUNDARY: Intra-sentential code-switch across whitespace boundary.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Exp A merges onset of Tamil verb 'Ġபண' while strictly respecting word space.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-26: `sprint planning முடிஞ்சிருச்சு` (intra_sentential_code_switch)
- **Technical Concern Summary:** Colloquial Tamil verb consumes 12 tokens due to lack of colloquial merges.
- **Original Input Text:** `sprint planning முடிஞ்சிருச்சு`
- **Original Candidate A Tokenization:** `s | p | r | in | t | Ġ | p | l | an | n | in | g | Ġà®® | à¯ģ | à® | Ł | à®¿ | à® | ŀ | à¯į | à® | ļ | à®¿ | à®° | à¯ģ | à® | ļ | à¯į | à® | ļ | à¯ģ`
- **Experimental Candidate A Tokenization:** `sp | rint | Ġp | l | ann | ing | Ġà®® | à¯ģ | à®Ł | à®¿ | à®ŀ | à¯į | à®ļ | à®¿ | à®° | à¯ģ | à®ļ | à¯į | à®ļ | à¯ģ`
- **Token IDs:**
  - Candidate A: `[94, 91, 93, 301, 95, 232, 91, 87, 280, 89, 301, 82, 279, 288, 268, 265, 272, 268, 264, 271, 268, 260, 272, 286, 288, 268, 260, 271, 268, 260, 288]`
  - Exp Candidate A: `[760, 1134, 299, 87, 388, 307, 310, 273, 278, 274, 848, 270, 317, 274, 284, 273, 317, 270, 317, 273]`
- **Token Counts:** Candidate A = 31 tokens | Exp Candidate A = 20 tokens (Reduction: 35.5%)
- **Unicode Codepoints:** `U+0073 U+0070 U+0072 U+0069 U+006E U+0074 U+0020 U+0070 U+006C U+0061 U+006E U+006E U+0069 U+006E U+0067 U+0020 U+0BAE U+0BC1 U+0B9F U+0BBF U+0B9E U+0BCD U+0B9A U+0BBF U+0BB0 U+0BC1 U+0B9A U+0BCD U+0B9A U+0BC1`
- **Grapheme-Boundary Observations:** 24 grapheme clusters; 28 codepoints.
- **Morphological Observations:** CLEAR_MORPHEME_BOUNDARY: Multi-word English noun phrase + colloquial Tamil completive verb.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Exp A achieves 35.5% compression without cross-language boundary leakage.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-27: `algorithm romba slow-ஆ இருக்கு` (intra_sentential_code_switch)
- **Technical Concern Summary:** Mixed-script sentence achieves 46.4% compression; Romanized adverb captured cleanly.
- **Original Input Text:** `algorithm romba slow-ஆ இருக்கு`
- **Original Candidate A Tokenization:** `al | g | o | r | i | th | m | Ġ | r | o | m | b | a | Ġ | s | lo | w | - | à® | Ĩ | Ġà® | ĩ | à®° | à¯ģ | à®ķ | à¯į | à®ķ | à¯ģ`
- **Experimental Candidate A Tokenization:** `al | gor | ith | m | Ġromba | Ġs | low | - | à®Ĩ | Ġà®ĩà®° | à¯ģ | à®ķ | à¯į | à®ķ | à¯ģ`
- **Token IDs:**
  - Candidate A: `[297, 82, 90, 93, 84, 293, 88, 232, 93, 90, 88, 77, 76, 232, 94, 302, 98, 24, 268, 240, 273, 241, 286, 288, 277, 271, 277, 288]`
  - Exp Candidate A: `[301, 1120, 493, 88, 633, 297, 1126, 24, 766, 631, 273, 272, 270, 272, 273]`
- **Token Counts:** Candidate A = 28 tokens | Exp Candidate A = 15 tokens (Reduction: 46.4%)
- **Unicode Codepoints:** `U+0061 U+006C U+0067 U+006F U+0072 U+0069 U+0074 U+0068 U+006D U+0020 U+0072 U+006F U+006D U+0062 U+0061 U+0020 U+0073 U+006C U+006F U+0077 U+002D U+0B86 U+0020 U+0B87 U+0BB0 U+0BC1 U+0B95 U+0BCD U+0B95 U+0BC1`
- **Grapheme-Boundary Observations:** 25 grapheme clusters; 28 codepoints.
- **Morphological Observations:** CLEAR_MORPHEME_BOUNDARY: Four-way code-mixing with Romanized Tamil adverb.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Exp A merges Romanized 'romba' as an atomic token ('Ġromba'), proving synthetic corpus capture.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-28: `Please check the logs da` (english_with_tamil_discourse_markers)
- **Technical Concern Summary:** Optimal tokenization efficiency achieved; discourse particle 'da' isolated cleanly.
- **Original Input Text:** `Please check the logs da`
- **Original Candidate A Tokenization:** `P | l | e | a | s | e | Ġ | c | he | c | k | Ġthe | Ġ | lo | g | s | Ġ | d | a`
- **Experimental Candidate A Tokenization:** `Please | Ġcheck | Ġthe | Ġlogs | Ġda`
- **Token IDs:**
  - Candidate A: `[59, 87, 80, 76, 94, 80, 232, 78, 291, 78, 86, 325, 232, 302, 82, 94, 232, 79, 76]`
  - Exp Candidate A: `[935, 484, 359, 914, 617]`
- **Token Counts:** Candidate A = 19 tokens | Exp Candidate A = 5 tokens (Reduction: 73.7%)
- **Unicode Codepoints:** `U+0050 U+006C U+0065 U+0061 U+0073 U+0065 U+0020 U+0063 U+0068 U+0065 U+0063 U+006B U+0020 U+0074 U+0068 U+0065 U+0020 U+006C U+006F U+0067 U+0073 U+0020 U+0064 U+0061`
- **Grapheme-Boundary Observations:** 19 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.
- **Morphological Observations:** CLEAR_MORPHEME_BOUNDARY: Grammatical English clause + colloquial Tamil pragmatic particle.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Exp A achieves optimal 1 token per word across entire sentence ('Please | Ġcheck | Ġthe | Ġlogs | Ġda').
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-29: `pannirukkom` (spoken_informal_tanglish_verbs)
- **Technical Concern Summary:** Romanized verbal morphology achieves 40% compression with meaningful sub-stems.
- **Original Input Text:** `pannirukkom`
- **Original Candidate A Tokenization:** `p | an | n | i | r | u | k | k | o | m`
- **Experimental Candidate A Tokenization:** `p | ann | iru | k | k | om`
- **Token IDs:**
  - Candidate A: `[91, 280, 89, 84, 93, 96, 86, 86, 90, 88]`
  - Exp Candidate A: `[91, 388, 424, 86, 86, 334]`
- **Token Counts:** Candidate A = 10 tokens | Exp Candidate A = 6 tokens (Reduction: 40.0%)
- **Unicode Codepoints:** `U+0070 U+0061 U+006E U+006E U+0069 U+0072 U+0075 U+006B U+006B U+006F U+006D`
- **Grapheme-Boundary Observations:** 11 grapheme clusters; single-byte ASCII. 0 cuts inside graphemes.
- **Morphological Observations:** CLEAR_MORPHEME_BOUNDARY: Romanized colloquial Tamil verbal morphology.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Exp A reduces from 10 single-letter tokens to 6 morphemic chunks ('p | ann | iru | k | k | om').
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

### OWN-REV-30: `கம்ப்யூட்டர்` (tamil_script_loanwords)
- **Technical Concern Summary:** Initial and final syllables merged, but internal consonant cluster remains fragmented.
- **Original Input Text:** `கம்ப்யூட்டர்`
- **Original Candidate A Tokenization:** `à®ķ | à®® | à¯į | à® | ª | à¯į | à®¯ | à¯ | Ĥ | à® | Ł | à¯į | à® | Ł | à®° | à¯į`
- **Experimental Candidate A Tokenization:** `à®ķà®® | à¯į | à®ª | à¯į | à®¯ | à¯Ĥ | à®Ł | à¯į | à®Łà®° | à¯į`
- **Token IDs:**
  - Candidate A: `[277, 278, 271, 268, 115, 271, 312, 270, 236, 268, 265, 271, 268, 265, 286, 271]`
  - Exp Candidate A: `[967, 270, 276, 270, 283, 396, 278, 270, 851, 270]`
- **Token Counts:** Candidate A = 16 tokens | Exp Candidate A = 10 tokens (Reduction: 37.5%)
- **Unicode Codepoints:** `U+0B95 U+0BAE U+0BCD U+0BAA U+0BCD U+0BAF U+0BC2 U+0B9F U+0BCD U+0B9F U+0BB0 U+0BCD`
- **Grapheme-Boundary Observations:** 7 grapheme clusters; 12 codepoints. All pulli marks detached.
- **Morphological Observations:** CLEAR_MORPHEME_BOUNDARY: Phonetic transliteration of technical loanword into Tamil script.
- **Reconstruction Status:** `EXACT_MATCH_100%` (Both tokenizers reconstruct bit-for-bit exact input text)
- **Known Limitations or Uncertainties:** Exp A merges initial syllable 'கம்' and terminal syllable 'டர்', reducing tokens from 16 to 10.
- **Owner Review Decision:** `NOT_REVIEWED`  
  *(Allowed: `OWNER_ACCEPTS_EXPERIMENTAL_SEGMENTATION` | `OWNER_ACCEPTS_ORIGINAL_SEGMENTATION` | `OWNER_ACCEPTS_BOTH` | `OWNER_REJECTS_BOTH` | `OWNER_REQUIRES_MORE_EVIDENCE`)*
- **Owner Rationale:** `""`

---

## 5. Owner Decision Instructions

1. Open [TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv](file:///C:/IGRIS/TOKENIZER_OWNER_REVIEW_DECISIONS_TEMPLATE.csv).
2. For each row (`OWN-REV-01` to `OWN-REV-30`), update `owner_decision` from `NOT_REVIEWED` to your chosen determination.
3. Record your technical rationale in `owner_rationale`.
4. Supporting evidence for all 300 test cases is indexed in [TOKENIZER_OWNER_REVIEW_EVIDENCE_INDEX.md](file:///C:/IGRIS/TOKENIZER_OWNER_REVIEW_EVIDENCE_INDEX.md).
