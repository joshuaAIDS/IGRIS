# IGRIS Production Multilingual Evaluation Dataset Specification

**Document Version**: 1.0.0  
**Milestone**: 3B.59 — Production Evaluation Readiness  
**Target Architecture**: IGRIS Decoder-Only Transformer (Context Length: 2,048, Vocabulary: 32,768)  
**Governance Scope**: Specification and quality framework only. **No production datasets or private training data were accessed during creation.**

---

## 1. Scope & Purpose

This specification defines the formal requirements, category coverage, quality criteria, and leakage prevention protocols for constructing the IGRIS production evaluation benchmark corpus. The evaluation dataset will be used to independently and comparatively evaluate Candidate A (ByteLevel BPE) and Candidate B (SentencePiece Unigram) under controlled governance once explicit human authorization is granted.

---

## 2. Category Coverage Requirements

The production evaluation dataset must comprise exactly 10 linguistic and structural categories, balanced across domain, length, and morphological complexity.

| ID | Category | Primary Script(s) | Target Samples | Target Word Volume | Target Char Volume | Minimum Coverage & Domain Scope |
|:---:|:---|:---|:---:|:---:|:---:|:---|
| **1** | **Tamil** | Tamil (`\u0B80`–`\u0BFF`) | $\ge 500$ | $\ge 100,000$ | $\ge 700,000$ | Classical literature, modern formal prose, administrative text, agglutinative inflections, Grantha ligatures (`ஸ்ரீ`, `க்ஷ`). |
| **2** | **English** | Latin (`\u0020`–`\u007F`) | $\ge 500$ | $\ge 120,000$ | $\ge 650,000$ | Technical prose, computer science literature, legal disclaimers, contractions (`shouldn't`, `we've`), diverse vocabulary. |
| **3** | **Tanglish** | Latin (`\u0020`–`\u007F`) | $\ge 300$ | $\ge 50,000$ | $\ge 300,000$ | Conversational Romanized Tamil, colloquial particles, developer code-switching, social messaging phrasing. |
| **4** | **Hindi** | Devanagari (`\u0900`–`\u097F`) | $\ge 400$ | $\ge 80,000$ | $\ge 500,000$ | Formal news, constitutional prose, complex conjuncts (`विश्वविद्यालय`, `दृष्टिकोण`), technical terminology. |
| **5** | **Other Indian Languages** | Telugu, Kannada, Malayalam, Bengali, Gujarati | $\ge 300$ | $\ge 50,000$ | $\ge 350,000$ | Indic script diversity across Dravidian and Indo-Aryan families; tests script transfer and byte-fallback robustness. |
| **6** | **Multilingual Mixed Text** | Mixed Indic + Latin | $\ge 300$ | $\ge 60,000$ | $\ge 400,000$ | Intra-sentential code-switching, parallel translations, multi-script system headers, bilingual documentation. |
| **7** | **Programming Code** | ASCII / UTF-8 | $\ge 400$ | $\ge 80,000$ | $\ge 500,000$ | Python, TypeScript/JavaScript, Rust, SQL, JSON/YAML schemas, regex patterns, structured indentation. |
| **8** | **Technical Documentation** | Markdown / UTF-8 | $\ge 300$ | $\ge 60,000$ | $\ge 450,000$ | REST API specifications, GitHub-flavored Markdown tables, warning alerts, system architecture notes, LaTeX math formulas. |
| **9** | **Conversational Text** | Multilingual | $\ge 300$ | $\ge 50,000$ | $\ge 300,000$ | Multi-turn chat dialogue, colloquial idioms, short queries, questions, imperative workflow instructions. |
| **10** | **Emoji & Unicode Edge Cases** | Unicode 15.1.0 | $\ge 200$ | $\ge 20,000$ | $\ge 150,000$ | ZWJ multi-person emoji sequences, combining diacritics, RTL marks, Indic ZWNJ/ZWJ ligatures, Plane 15/16 high codepoints. |
| **Total** | **Full Benchmark Corpus** | **Multilingual** | **$\ge 3,500$** | **$\ge 670,000$** | **$\ge 4,300,000$** | **Comprehensive Production Evaluation Corpus** |

---

## 3. Sample Selection & Stratification Methodology

1. **Length Stratification**:
   To rigorously test tokenizer behavior across context scales, each category must distribute samples across four distinct sequence tiers:
   - **Short (Tier 1)**: 1 to 64 tokens ($25\%$ of category samples) — tests prompt handling, single sentences, and boundary isolation.
   - **Medium (Tier 2)**: 65 to 1,024 tokens ($50\%$ of category samples) — tests standard paragraphs, function definitions, and dialogue turns.
   - **Long (Tier 3)**: 1,025 to 2,048 tokens ($20\%$ of category samples) — tests dense articles, long documentation sections, and full context utilization.
   - **Overflow (Tier 4)**: $> 2,048$ tokens ($5\%$ of category samples) — tests sliding-window chunking, truncation behavior, and boundary stability.

2. **Domain Diversity**:
   Samples within each category must be drawn from at least 3 distinct domain registers (e.g. academic/scientific, journalistic/formal, and colloquial/informal) to avoid domain-specific vocabulary bias.

---

## 4. Character Encoding & Unicode Normalization Policy

1. **Character Encoding**:
   - Strictly valid **UTF-8** encoding across all bytes.
   - Zero Byte Order Marks (BOM: `\uFEFF` is stripped if present).
   - Rejection of invalid UTF-8 byte sequences.
   - Rejection of lone surrogate codepoints (`U+D800` through `U+DFFF`), which are illegal in well-formed UTF-8.

2. **Unicode Normalization Policy**:
   - **Default Evaluation Mode**: Strictly canonical **NFC** (Normalization Form C) per Unicode 15.1.0 (`unicodedata2==15.1.0`).
   - Decomposed sequences (NFD) must be detected and converted to NFC prior to tokenization.
   - **Exact Mode Evaluation**: The evaluation harness must also run an exact-codepoint pass (`StrictTokenizer(..., normalization='exact')`) to verify that non-NFC codepoints round-trip without loss when NFC conversion is bypassed.
   - **Structural Sentinel Escaping**: The escape sentinel `U+F0000` must be used strictly for literal structural token spellings (`<|user|>`, `<think>`, etc.) to ensure structural token isolation.

---

## 5. Deduplication & Near-Duplicate Detection

1. **Exact Deduplication**:
   - Every candidate sample is normalized to NFC, stripped of leading/trailing whitespace, and hashed using cryptographic **SHA-256**.
   - Samples with colliding SHA-256 hashes within or across categories are rejected as redundant duplicates.

2. **Near-Duplicate Detection (MinHash + Jaccard)**:
   - Character 5-grams and word 3-grams are generated for every candidate sample.
   - A 64-permutation MinHash signature is computed using universal hashing.
   - Pairs exhibiting estimated Jaccard similarity $\ge 0.85$ are flagged for manual review or deduplicated to preserve sample entropy.

---

## 6. Data Quality Checks

Prior to corpus acceptance, every sample must pass automated filtering implemented in `scripts/dataset_quality_checks.py`:
1. **Minimum Length**: Sample text must contain $\ge 10$ non-whitespace characters.
2. **Noise Ratio Gate**: Non-linguistic characters (symbols, control characters, isolated punctuation) must not exceed $25\%$ of non-whitespace characters, except in Category 7 (Programming Code) and Category 10 (Emoji/Unicode).
3. **Control Character Audit**: ASCII control characters (`\x00`–`\x08`, `\x0B`–`\x0C`, `\x0E`–`\x1F`, `\x7F`) are strictly prohibited; standard whitespace (`\t`, `\n`, `\r`) is preserved.
4. **Line Integrity**: Line breaks must be standardized to `\n` (CRLF normalized).

---

## 7. Train / Evaluation Leakage Prevention

To guarantee independent, unbiased evaluation of the final models:
1. **Cryptographic Hash Cross-Checks**:
   - The SHA-256 hash set of all evaluation samples must be cross-referenced against the master hash inventory of all training data candidates.
   - Any sample whose hash matches a training record is permanently removed from the evaluation set.
2. **N-Gram Containment Audit**:
   - String containment checks for any exact match of length $\ge 80$ characters between evaluation samples and known training corpus inventories.
3. **Contamination Lock**:
   - The approved evaluation dataset must be cryptographically locked with a published SHA-256 manifest and stored in an isolated, read-only location.
