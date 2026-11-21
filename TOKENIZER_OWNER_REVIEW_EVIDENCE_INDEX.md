# IGRIS Tokenizer Owner Review Evidence Index

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
