# PHASE 23A — SYNTHETIC TANGLISH GENERATOR ARCHITECTURE & DESIGN SPECIFICATION
## Procedural, Non-Scraped Synthetic Data Generation for Tamil-English Code-Mixed Language

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-19  
**Status:** SPECIFIED, IMPLEMENTED & VERIFIED  

---

## 1. Linguistic Scope and Definition

Tanglish represents the natural code-mixed and code-switched linguistic variety combining **Tamil** (`ta` / `TAMIL`) and **English** (`en` / `ENGLISH`). It is widely used in informal digital communication, technical environments, and conversational media.

### Five Approved Linguistic Categories:
1. **`TAMIL_SCRIPT_ENGLISH_TECH` (Tamil Script with English Loanwords):**
   - Written in the standard Tamil script (`U+0B80`–`U+0BFF`).
   - Integrates English technical vocabulary, computing terminology, or everyday loanwords with Tamil agglutinative postpositions (e.g., `-ஐ`, `-க்கு`, `-இல்`, `-ஆல்`, `-ஆ`, `-உடன்`).
   - Example: *"இந்த server configuration ரொம்ப complex-ஆ இருக்கு, restart பண்ணவா?"*
2. **`ROMANIZED_TAMIL_INFORMAL` (Romanized Tamil / `ta-Latn`):**
   - Spoken colloquial Tamil transcribed phonetically into Latin script.
   - Contains colloquial Tamil morphology and phonetic conventions without English syntactic framing.
   - Example: *"Innaiku evening tea sapda polama? Enaku romba tired-ah iruku."*
3. **`ENGLISH_TAMIL_COLLOQUIAL` (English with Tamil Discourse Particles):**
   - English grammatical base incorporating characteristic Tamil discourse particles, vocatives, and emotional markers (*da*, *pa*, *machan*, *aiyo*, *seri*, *apdiya*, *romba*, *kandippa*).
   - Example: *"Let us wrap up this release quickly da, otherwise deployment will get delayed."*
4. **`INTRA_SENTENTIAL_CODE_SWITCH` (Alternating Code-Switching):**
   - Rapid alternation of Tamil and English phrases within clause and sentence boundaries.
   - Example: *"Client requirement-la sudden change, so frontend layout-ஐ restructure பண்ண வேண்டியிருக்கு."*
5. **`FORMAL_TECHNICAL_TANGLISH` (Formal Technical Glossing):**
   - Formal engineering, academic, or administrative prose using bilingual glosses and formal technical terminology.
   - Example: *"கணினி வலையமைப்பு (computer network) பாதுகாப்பு protocol-கள் முறையாக configure செய்யப்பட வேண்டும்."*

---

## 2. Generator Design & Safety Invariants

```mermaid
flowchart LR
    A["Procedural Generator"] --> B["Linguistic Template Engine"]
    B --> C["Metadata & Script Analyzer"]
    C --> D["Quality & Security Filter"]
    D --> E["PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl"]
    
    subgraph Quality Gates
        D1["Unicode NFC Validation"]
        D2["Prohibited Script Scanner"]
        D3["PII & Privacy Checker"]
        D4["Exact Deduplication"]
    end
    D --- Quality Gates
```

### Strict Architectural Invariants:
1. **Zero Scraping & External Downloads:** The pipeline runs entirely in-process using handcrafted linguistic templates. No web scrapers, YouTube APIs, or third-party datasets are invoked.
2. **Zero Living PII:** No real names, phone numbers, email addresses, personal usernames, or identifiable personal histories are included.
3. **Zero Prohibited Script Contamination:** Every fixture is validated to ensure 0% character contamination from non-target language scripts:
   - Devanagari (`U+0900`–`U+097F`) — strictly prohibited.
   - Telugu (`U+0C00`–`U+0C7F`) — strictly prohibited.
   - Kannada (`U+0C80`–`U+0CFF`) — strictly prohibited.
   - Malayalam (`U+0D00`–`U+0D7F`) — strictly prohibited.
   - Bengali, Gujarati, Gurmukhi, Oriya, Arabic, Cyrillic, CJK — strictly prohibited.
4. **Unicode Normalization:** All text is canonicalized to **Unicode NFC** (Canonical Decomposition, followed by Canonical Composition).
5. **Distributional Disclaimer:**
   > **Explicit Disclaimer:** These synthetic fixtures are designed strictly for unit testing, tokenizer boundary analysis, script classification validation, and architectural staging. They do not claim to represent empirical population-level demographic or sociolinguistic language distributions.

---

## 3. Fixture Schema

Each fixture in `PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl` follows a strict schema:
```json
{
  "id": "SYN-TG-001",
  "category": "TAMIL_SCRIPT_ENGLISH_TECH",
  "register": "informal",
  "code_switch_type": "intra_sentential",
  "text": "இந்த server configuration ரொம்ப complex-ஆ இருக்கு, restart பண்ணவா?",
  "script_composition": {
    "total_chars": 64,
    "tamil_chars": 35,
    "latin_chars": 22,
    "punct_space_chars": 7,
    "tamil_ratio": 0.5469,
    "latin_ratio": 0.3438
  },
  "quality_checks": {
    "unicode_nfc_valid": true,
    "zero_non_target_contamination": true,
    "zero_pii": true,
    "non_empty_clean": true
  }
}
```

---

## 4. Production Isolation Guarantee

The generated synthetic fixtures are stored strictly in `PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl` within the patch and artifact documentation directories. They are **NOT** added to the production data queue, quarantine staging, or pretraining shards.
