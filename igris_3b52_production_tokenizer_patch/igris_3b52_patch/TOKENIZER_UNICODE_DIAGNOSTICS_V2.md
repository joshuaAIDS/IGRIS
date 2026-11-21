# IGRIS Tokenizer Technical Unicode Diagnostics (V2)

**Document Version:** 2.0.0 (Corrected & Technically Validated)  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Target Languages:** Strictly Tamil, English, Tanglish  
**Evaluated Artifacts:**
- **Candidate A (Selected Production Tokenizer):** SHA256 `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561`
- **Experimental Candidate A (Synthetic-Trained Copy):** SHA256 `3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce`
- **Reference Candidate B (SentencePiece Unigram):** SHA256 `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888`

---

## 1. Executive Summary & Epistemic Classification

This document provides the definitive technical validation of the ByteLevel BPE tokenizer artifacts for the IGRIS multilingual decoder-only Transformer, correcting previous speculative claims and distinguishing verified facts, unresolved technical tensions, and open research hypotheses.

```
                           EPISTEMIC CLASSIFICATION OF FINDINGS
                                             │
               ┌─────────────────────────────┼─────────────────────────────┐
               ▼                             ▼                             ▼
       VERIFIED FACTS               UNRESOLVED ISSUES                 HYPOTHESES
   • 100.0% round-trip decode   • Overmerging in English       • Detached pulli improves
   • Zero pipeline normalizer     compounds (microservice)       grammatical reasoning
   • Byte-to-Unicode mapping    • Single-token UTF-8 invalidity• Complete chars inside tokens
     is standard GPT-2/HF         in Candidate A baseline        guarantee linguistic superiority
   • 4 boundary levels are      • Sensitivity to NFC vs NFD    • Lower fertility automatically
     distinct concepts            on Tamil 'கௌ' (AU sign)        indicates better segmentation
```

---

## 2. Corrected ByteLevel BPE Architecture & Mapping

### A. The Core ByteLevel BPE Principle
> [!IMPORTANT]
> **CORRECTED ARCHITECTURAL FACT:**  
> In ByteLevel BPE (GPT-2, GPT-4, LLaMA-3), **individual BPE tokens do NOT need to contain complete UTF-8 characters.**  
> BPE is an arbitrary byte-stream encoder. A token is simply an index mapped to a string of 1 or more bytes. The tokenizer contract requires only that the concatenated byte stream decodes to the original string.

The printable character representations (e.g. `à®¤`, `à¯į`, `Ġ`) are produced by the standard invertible byte-to-Unicode bijection $f: [0, 255] \leftrightarrow \Sigma_{\text{printable}}$:

```python
def bytes_to_unicode():
    bs = (
        list(range(ord("!"), ord("~") + 1))       # 0x21 to 0x7E (printable ASCII)
        + list(range(ord("¡"), ord("¬") + 1))     # 0xA1 to 0xAC (Latin-1 printable)
        + list(range(ord("®"), ord("ÿ") + 1))     # 0xAE to 0xFF (Latin-1 printable)
    )
    cs = bs[:]
    n = 0
    for b in range(2**8):
        if b not in bs:
            bs.append(b)
            cs.append(2**8 + n)                   # Maps non-printable bytes to U+0100 onward
            n += 1
    return dict(zip(bs, [chr(c) for c in cs]))
```

### B. Representative Tamil Byte Reconstruction Audit
The table below documents exact byte sequences, token IDs, individual token bytes, reconstructed byte streams, and decoded strings from [TOKENIZER_BYTELEVEL_MAPPING_AUDIT.csv](file:///C:/IGRIS/TOKENIZER_BYTELEVEL_MAPPING_AUDIT.csv):

| Input String | Raw UTF-8 Bytes (Hex) | Tokenizer | Token IDs | Token Strings | Token Bytes (Hex) | Reconstructed UTF-8 | Decoded Text | Reconstruct Match? |
|:---|:---|:---:|:---|:---|:---|:---|:---:|:---:|
| `க்` | `E0 AE 95 E0 AF 8D` | **Cand A** | `[277, 271]` | `à®ķ \| à¯į` | `E0 AE 95 \| E0 AF 8D` | `E0 AE 95 E0 AF 8D` | `க்` | **TRUE** |
| `க்` | `E0 AE 95 E0 AF 8D` | **Exp A** | `[272, 270]` | `à®ķ \| à¯į` | `E0 AE 95 \| E0 AF 8D` | `E0 AE 95 E0 AF 8D` | `க்` | **TRUE** |
| `கௌ` | `E0 AE 95 E0 AF 8C` | **Cand A** | `[277, 270, 246]` | `à®ķ \| à¯ \| Į` | `E0 AE 95 \| E0 AF \| 8C` | `E0 AE 95 E0 AF 8C` | `கௌ` | **TRUE** |
| `கௌ` | `E0 AE 95 E0 AF 8C` | **Exp A** | `[272, 1147]` | `à®ķ \| à¯Į` | `E0 AE 95 \| E0 AF 8C` | `E0 AE 95 E0 AF 8C` | `கௌ` | **TRUE** |
| `செய்தல்` | `E0 AE 9A E0 AF 86 E0 AE AF E0 AF 8D E0 AE A4 E0 AE B2 E0 AF 8D` | **Cand A** | `[268, 260, 270, 240, 312, 271, 282, 294, 271]` | `à® \| ļ \| à¯ \| Ĩ \| à®¯ \| à¯į \| à®¤ \| à®² \| à¯į` | `E0 AE \| 9A \| E0 AF \| 86 \| E0 AE AF \| E0 AF 8D \| E0 AE A4 \| E0 AE B2 \| E0 AF 8D` | `E0 AE 9A E0 AF 86 E0 AE AF E0 AF 8D E0 AE A4 E0 AE B2 E0 AF 8D` | `செய்தல்` | **TRUE** |
| `செய்தல்` | `E0 AE 9A E0 AF 86 E0 AE AF E0 AF 8D E0 AE A4 E0 AE B2 E0 AF 8D` | **Exp A** | `[317, 325, 283, 270, 652, 270]` | `à®ļ \| à¯Ĩ \| à®¯ \| à¯į \| à®¤à®² \| à¯į` | `E0 AE 9A \| E0 AF 86 \| E0 AE AF \| E0 AF 8D \| E0 AE A4 E0 AE B2 \| E0 AF 8D` | `E0 AE 9A E0 AF 86 E0 AE AF E0 AF 8D E0 AE A4 E0 AE B2 E0 AF 8D` | `செய்தல்` | **TRUE** |

**Empirical Finding:** In Candidate A, token `à®` consists of `0xE0 0xAE` (an incomplete 2-byte prefix), and token `ļ` consists of `0x9A` (a trailing byte). While neither token is valid UTF-8 in isolation, their concatenation is `0xE0 0xAE 0x9A` (`ச`), which decodes with 100.0% exact fidelity. In Exp Candidate A, these byte bigrams are merged into complete character tokens (`à®ļ`), but both tokenizers adhere strictly to ByteLevel BPE specifications.

---

## 3. The Four Distinct Levels of Linguistic & Structural Boundaries

A major source of conceptual confusion in tokenizer evaluations is conflating distinct boundary levels. The table below formalizes the four boundary tiers evaluated in [TOKENIZER_GRAPHEME_BOUNDARY_AUDIT.csv](file:///C:/IGRIS/TOKENIZER_GRAPHEME_BOUNDARY_AUDIT.csv):

```
+───────────────────────────────────────────────────────────────────────────────────────────────+
|                                HIERARCHY OF SEGMENTATION BOUNDARIES                           |
+───────────────────────────────+───────────────────────────────────────────────────────────────+
| Boundary Tier                 | Technical Definition & Indic Script Context                   |
+───────────────────────────────+───────────────────────────────────────────────────────────────+
| 1. Byte Boundary              | Division between raw 8-bit octets in UTF-8 (e.g. 0xE0 | 0xAE) |
| 2. Unicode Code-Point         | Division between atomic Unicode scalar values (U+0B95 | U+0BCD)|
| 3. Grapheme-Cluster           | Division between perceived orthographic syllables (UAX #29 \X)|
| 4. Linguistic Morpheme        | Division between semantic/grammatical units (root + affix)    |
+───────────────────────────────+───────────────────────────────────────────────────────────────+
```

### Comparative Boundary Analysis:
1. **Tamil Consonant + Pulli (`க்`):**
   - **Bytes:** 6 bytes (`E0 AE 95 E0 AF 8D`)
   - **Codepoints:** 2 codepoints (`U+0B95` + `U+0BCD`)
   - **Grapheme Clusters:** **1 cluster** (`க்`)
   - **Morphemes:** 2 morphemes (consonant base + vowel suppression marker)
   - **Tokenizer Cut:** Both tokenizers cut between `U+0B95` and `U+0BCD`. This cut **respects** code-point and morpheme boundaries, but **splits** the single grapheme cluster!
2. **Tamil Uyirmei Vocalized Syllable (`தி`):**
   - **Bytes:** 6 bytes (`E0 AE A4 E0 AE BF`)
   - **Codepoints:** 2 codepoints (`U+0BA4` + `U+0BBF`)
   - **Grapheme Clusters:** **1 cluster** (`தி`)
   - **Tokenizer Cut:** Exp A cuts between `த` and `ி` (`à®¤ | à®¿`). It splits the grapheme cluster, but preserves individual codepoints.
3. **English Closed Compound (`microservice`):**
   - **Bytes = Codepoints = Grapheme Clusters:** 12 single-byte ASCII characters.
   - **Morphemes:** 2 morphemes (`micro` + `service`).
   - **Tokenizer Cut:** Exp A segments as `m | icroser | vice`. It respects byte, codepoint, and grapheme boundaries, but **violates the linguistic morpheme boundary**!

---

## 4. Pipeline Normalization Audit: NFC vs NFD

### Confirmed Configuration:
Inspection of `tokenizer.json` for both `candidate_a` and `candidate_a_synthetic_experiment` reveals:
```json
"normalizer": null
```
**Neither tokenizer implements input normalization.** The tokenizer encodes the exact bytes passed to it.

### Empirical Normalization Findings (from [TOKENIZER_NORMALIZATION_AUDIT.csv](file:///C:/IGRIS/TOKENIZER_NORMALIZATION_AUDIT.csv)):
1. **Tamil Script Invariance:**
   For pure consonants, vowel signs, Grantha characters, compounds, and inflections (`க்`, `ஸ்ரீ`, `செய்தல்`, `வந்தேன்`, `மரங்கள்`, `பல்கலைக்கழகம்`, `server-ல்`), **NFC and NFD codepoints are 100% identical.** Tamil Unicode combining characters have no composite precomposed equivalents.
2. **The `கௌ` Exception (AU Vowel Sign):**
   The only Tamil character where NFC $\neq$ NFD is `கௌ`:
   - **NFC:** `U+0B95 U+0BCC` (2 codepoints) $\to$ Exp A produces 2 tokens (`à®ķ | à¯Į`).
   - **NFD:** `U+0B95 U+0BC6 U+0BD7` (3 codepoints) $\to$ Exp A produces 4 tokens (`à®ķ | à¯Ĩ | à¯ | Ĺ`).
3. **Accented Latin Script:**
   In loanwords (`café`, `naïve`), NFC forms produce 4–5 tokens, while NFD decomposed forms produce 5–6 tokens.
4. **Reconstruction Fidelity:**
   Because `normalizer: null`, both tokenizers reconstruct NFC input as exact NFC and NFD input as exact NFD with **100.0% round-trip fidelity**.

---

## 5. Correction of Speculative Conclusions

To maintain rigorous scientific standards, previous speculative interpretations are formally corrected and reclassified:

| Previous Statement / Claim | Scientific Classification | Verified Technical Correction |
|:---|:---:|:---|
| *"Detached pulli tokens improve grammatical reasoning"* | **UNSUPPORTED HYPOTHESIS** | Detached pulli allows the subword vocabulary to share representations between pure consonants (`க்`) and vocalized syllables (`க`, `கி`), but it doubles sequence length for every consonant cluster. Downstream reasoning quality can only be determined empirically through transformer pretraining probes. |
| *"Complete UTF-8 characters inside tokens guarantee linguistic superiority"* | **UNSUPPORTED HYPOTHESIS** | In ByteLevel BPE, tokens represent byte n-grams. Sequence-level decodability ($D(E(x)) = x$) is mathematically sufficient. Individual token UTF-8 completeness facilitates single-token inspection, but does not guarantee superior representations. |
| *"Lower token counts automatically indicate better segmentation"* | **CLASSIC BPE FALLACY** | Lower token count measures sequence compression. Unconstrained compression leads to overmerging (e.g. `icroser` in `microservice`), which harms compositionality and out-of-domain generalization. |

---

## 6. English Overmerging Audit

Detailed evaluation in [TOKENIZER_OVERMERGING_AUDIT.csv](file:///C:/IGRIS/TOKENIZER_OVERMERGING_AUDIT.csv) reveals:
- **`microservice`:** `['m', 'icroser', 'vice']` — **CRITICAL OVERMERGE.** The token `icroser` spans the compound boundary between prefix `micro-` and root `service`.
- **`microservices`:** `['m', 'icroser', 'vices']` — Overmerge repeats consistently across plural inflection.
- **`asynchronous`:** `['as', 'ynchronous']` — **NON-MORPHEMIC MERGE.** Merges privative prefix `a-` with root onset `s-`, obscuring the negation morpheme.
- **`middleware`:** `['m', 'id', 'd', 'le', 'ware']` — **CLEAN COMPOUND BOUNDARY.** Suffix `ware` is an intact atomic token; compound boundary is strictly preserved.
- **`internationalization`:** `['in', 'tern', 'ational', 'ization']` — Derivational suffixes `-ational` and `-ization` align with English morphological boundaries.
- **`unavoidable`:** `['un', 'av', 'o', 'id', 'able']` — Prefix `un` and suffix `able` are preserved as exact atomic tokens.

---

## 7. Comprehensive Findings Matrix

| Finding / Property | Epistemic Status | Verification Evidence |
|:---|:---:|:---|
| **Round-Trip Decode Accuracy** | **VERIFIED FACT** | 100.0% bit-for-bit reconstruction across all evaluation datasets |
| **ByteLevel BPE Mapping** | **VERIFIED FACT** | Matches GPT-2/HF bijective byte-to-Unicode mapping |
| **Pipeline Normalizer** | **VERIFIED FACT** | Explicitly confirmed `normalizer: null` in both tokenizers |
| **NFC vs NFD Sensitivity** | **VERIFIED FACT** | Affects `கௌ` and accented Latin words; zero impact on other Tamil words |
| **English Overmerging Hazard** | **VERIFIED FACT** | Documented in `microservice` (`icroser`) and `asynchronous` (`as`) |
| **Tanglish Boundary Health** | **VERIFIED FACT** | Zero cross-script boundary leakage across all 10 Tanglish test cases |
| **Pulli Representation Reasoning Impact** | **HYPOTHESIS** | Requires downstream pretraining evaluation to establish |
| **Token UTF-8 Validity Representation Impact** | **HYPOTHESIS** | BPE requires sequence-level decodability; single-token impact unverified |
| **Lower Fertility Quality Correlation** | **HYPOTHESIS** | Compression must be balanced against compositionality |
