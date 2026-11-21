# PHASE 31A — PRIVACY MASKING POLICY SPECIFICATION

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Date:** 2026-11-20  

---

## 1. Approved Placeholders & Non-Destructive Replacement

The project owner has approved two standardized masking placeholders:
* **Email Address:** `[EMAIL_REDACTED]`
* **Telephone Number:** `[PHONE_REDACTED]`

### Strict Replacement Requirements:
1. **Targeted Span Replacement:** Masking is applied only to the exact character start and end offsets of identified PII entities.
2. **Unicode Integrity:** Masking operates on Unicode NFC-normalized text. Surrounding Tamil characters, viramas, and vowel combining marks are strictly preserved without grapheme corruption.
3. **Machine-Readable Audit Record:** Each masking event generates a structured audit log containing:
   - `entity_type` (`EMAIL` or `PHONE`)
   - `placeholder` (`[EMAIL_REDACTED]` or `[PHONE_REDACTED]`)
   - `start_offset` and `end_offset`
   - `entity_hash` (One-way SHA-256 digest; *the raw personal data is never retained in ordinary logs*).
4. **False-Positive Guard:** Code syntax containing `@` (e.g. `A @ B` matrix multiplication, `@property` decorators) is protected from false-positive substitution.

---

## 2. Uncertain PII & Sensitive Narrative Policies

```
+-----------------------------------------------------------------------------------------+
| UNCERTAIN PII & SENSITIVE NARRATIVE HANDLING                                            |
+-----------------------------------------------------------------------------------------+
|  Ambiguous Identifiers (e.g. user_id_*, handle_*):   MANUAL_REVIEW_REQUIRED             |
|  Sensitive Narratives (health, finance disclosures): MANUAL_REVIEW_REQUIRED             |
|  Silent Acceptance:                                  STRICTLY FORBIDDEN                 |
|  Qualification:                                      Regex & NER do NOT provide         |
|                                                      complete privacy protection        |
+-----------------------------------------------------------------------------------------+
```

* **No Silent Acceptance:** Any text exhibiting unstructured sensitive narratives or ambiguous personal identifiers is routed to `MANUAL_REVIEW_REQUIRED`.

---

## 3. Synthetic Fixture Verification
Verified across 9 synthetic privacy test cases in `scripts/phase31a_policy_validator.py`:
- Single email masked cleanly; raw email absent from audit log.
- Multiple emails masked cleanly in reverse offset order.
- Phone number masked cleanly.
- Email and phone masked together.
- False-positive `@` code syntax preserved without replacement.
- Tamil Unicode surrounding email preserved in 100% stable NFC form.
- Overlapping/adjacent emails replaced without offset corruption.
- Uncertain user handle assigned `MANUAL_REVIEW_REQUIRED`.
- Sensitive health disclosure narrative assigned `MANUAL_REVIEW_REQUIRED`.
