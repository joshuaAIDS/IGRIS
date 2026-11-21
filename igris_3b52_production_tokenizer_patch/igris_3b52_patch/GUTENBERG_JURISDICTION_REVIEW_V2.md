# IGRIS Project Gutenberg Multi-Jurisdictional Legal Review (Version 2)

**Document Version:** 2.0.0  
**Status:** Canonical Multi-Jurisdictional Protocol (Milestone 3C.8)  
**Governing Laws:** US Copyright Act (17 U.S.C.), Indian Copyright Act 1957, UK/EU Copyright Directives  
**Target Corpora:** `SRC-EN-01` (Project Gutenberg Open Archive), `SRC-CV-06` (Project Gutenberg Theatrical Dialogue)  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)  
**Acquisition Status:** `NOT AUTHORIZED`  
**Human Approvals Status:** `PENDING` (Unsigned — Never Fabricate Signatures)

---

## 1. Statutory Corrections & Multi-Jurisdictional Framework

Milestone 3C.7 introduced the requirement of item-level review for Project Gutenberg texts. Version 2.0.0 formally updates the jurisdictional analysis to incorporate the correct Indian statutory framework under **The Copyright Act, 1957**.

### 1.1 The Tri-Jurisdictional Reality
Project Gutenberg hosts texts digitized under **United States copyright law**, where works published before 1928 are in the public domain. However, AI models trained on or evaluated against these texts are targeted for international deployment. Three distinct legal regimes govern the rights:

1. **United States**: Publication date rule (works published **before 1928** are in the public domain).
2. **India**: **Section 22 of The Copyright Act, 1957** prescribes a **Life + 60 years** term (author death year **$\le 1965$** for public domain entry in 2026).
3. **United Kingdom & European Union**: Berne Convention standard of **Life + 70 years** (author death year **$\le 1955$** for public domain entry in 2026).

```
+----------------------------------------------------------------------------------------------------+
|                         JURISDICTIONAL THRESHOLD DIVERGENCE (2026)                                 |
+----------------------------------------------------------------------------------------------------+
  Jurisdiction   Statutory Rule             2026 Public Domain Cut-Off Threshold
  ------------   --------------             ------------------------------------
  United States  Publication Date           First published before 1928
  India          Life + 60 (Sec 22)         Author died on or before December 31, 1965 (<= 1965)
  UK & EU        Life + 70 (Directives)     Author died on or before December 31, 1955 (<= 1955)
```

> [!CAUTION]
> **GOVERNANCE RULING**:
> **Never claim zero copyright risk globally for Project Gutenberg.**
> A work published in 1925 in New York by an author who died in 1962 is:
> - **Public Domain in the United States** (pre-1928 publication).
> - **Public Domain in India** (author died $\le 1965$, entered PD on Jan 1, 2023).
> - **UNDER COPYRIGHT in the UK and European Union** (Life+70 term expires Dec 31, 2032; protected until Jan 1, 2033).
> Distributing model weights trained on such a work in London, Paris, or Berlin would constitute copyright infringement.

---

## 2. Four Pillars of Item-Level Clearance

To clear an individual Gutenberg text file for evaluation or training, data custodians must verify all four independent rights layers:

### Pillar 1: Author Rights & Vital Dates
- **Sole Authorship**: Author's exact death year must be determined from official registers (VIAF, Library of Congress).
- **Joint Authorship**: Under Section 22 of the Indian Copyright Act, 1957 and Article 1 of EU Directive 2006/116/EC, copyright runs from the death of the **longest-surviving co-author**. All co-authors must have died on or before the cut-off year.
- **Anonymous / Pseudonymous Works**: Under Indian Section 23, the 60-year term runs from first publication, provided true author identity is never disclosed.

### Pillar 2: Translator & Derivative Rights
- A translation is legally an adaptation and constitutes a separate copyright work.
- If an ancient text (e.g., Homer, Sophocles, Dante) is translated into English, the **translator's death date** dictates the copyright term of that English text.
- Example: Constance Garnett translated Leo Tolstoy's works. Tolstoy died in 1910 (PD globally), but Garnett died in **1946**. In 2026, Garnett's translations are in the public domain in India ($1946 + 60 = 2006$) and the UK/EU ($1946 + 70 = 2016$). However, a translator who died in 1958 would remain under copyright in the UK/EU until 2029!

### Pillar 3: Publication & Posthumous Status
- Under Section 24 of the Indian Copyright Act, 1957, if a work is published posthumously, copyright subsists for **60 years from the date of first publication**, regardless of when the author died.
- Data custodians must verify that the specific edition was published during the author's lifetime or that 60+ years have elapsed since posthumous publication.

### Pillar 4: Editorial, Critical, and Adaptation Rights
- Modern critical editions, theatrical adaptations, stage directions, explanatory glosses, and abridgments carry distinct copyright owned by editors, adaptors, or theatrical companies.
- In `SRC-CV-06` (Project Gutenberg Theatrical Dialogue), theatrical texts must be examined to ensure no modern 20th-century stage directions or copyright-encumbered adaptations are present.

---

## 3. Project Gutenberg Trademark & Licensing Compliance

### 3.1 PGLAF Trademark Restrictions
"Project Gutenberg" is a registered trademark of the Project Gutenberg Literary Archive Foundation (PGLAF). The trademark persists indefinitely and is completely independent of the copyright status of the underlying text.

### 3.2 Mandatory Automated De-Branding Protocol
Under Section 1.E of the Project Gutenberg license, to use or redistribute the text outside the trademark terms:
1. **Header Stripping**: Programmatically remove all text preceding:
   `*** START OF THE PROJECT GUTENBERG EBOOK <TITLE> ***`
2. **Footer Stripping**: Programmatically remove all text from:
   `*** END OF THE PROJECT GUTENBERG EBOOK <TITLE> ***`
3. **Regex Sanity Sweep**: Search and purge all instances of `(?i)project\s+gutenberg`, donation requests, and PGLAF address blocks.
4. **Independent Checksum**: The cryptographic SHA-256 manifest hash must be computed strictly on the sanitized text body.

---

## 4. Multi-Jurisdictional Decision Workflow

```
+----------------------------------------------------------------------------------------------------+
|                         GUTENBERG ITEM-LEVEL CLEARANCE WORKFLOW (V2)                               |
+----------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
                     [Step 1: Record Work Title, Author, Translator, Pub Year]
                                                  |
                                                  v
                     [Step 2: Check US Public Domain Status (Pub < 1928)]
                                                  |
                     +----------------------------+----------------------------+
                     | No                                                      | Yes
                     v                                                         v
             [REJECT: US Protected]                   [Step 3: Check Lifetime vs Posthumous Publication]
                                                                               |
                                                  +----------------------------+----------------------------+
                                                  | Posthumous (Indian Sec 24)                              | Lifetime Publication
                                                  v                                                         v
                                  [Check: Pub Year + 60 <= 2025?]                           [Step 4: Check Last Co-Author Death]
                                  (If no -> REJECT)                                                         |
                                                                                +---------------------------+---------------------------+
                                                                                | Last Death > 1965                                     | Last Death <= 1965
                                                                                v                                                       v
                                                                     [REJECT: India Protected]                         [Step 5: Check UK/EU Cut-off (Death <= 1955)]
                                                                                                                                |
                                                                                                    +---------------------------+---------------------------+
                                                                                                    | Death 1956-1965                                       | Death <= 1955
                                                                                                    v                                                       v
                                                                                         [CONDITIONAL: India/US Only]                    [Step 6: Check Translator Death <= 1955]
                                                                                         (Banned from UK/EU deployment)                             |
                                                                                                                                                    v
                                                                                                                                 [Step 7: Strip PGLAF Headers & TM]
                                                                                                                                                    |
                                                                                                                                                    v
                                                                                                                                 [APPROVED FOR MANIFEST GENERATION]
```

---

## 5. Sample Item-Level Multi-Jurisdictional Audit

| EBook ID | Work Title | Author | First Pub Year | Author Death Year | US Status | India Status (Sec 22) | UK/EU Status (Life+70) | Global Release Clearance |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **#1524** | *Hamlet* | William Shakespeare | 1603 | 1616 | Public Domain | Public Domain | Public Domain | **CLEARED (Global Public Domain)** |
| **#844** | *The Importance of Being Earnest* | Oscar Wilde | 1895 | 1900 | Public Domain | Public Domain | Public Domain | **CLEARED (Global Public Domain)** |
| **#3825** | *Pygmalion* | George Bernard Shaw | 1913 | 1950 | Public Domain | Public Domain | Public Domain | **CLEARED (Global Public Domain)** |
| **#1112** | *The School for Scandal* | Richard Brinsley Sheridan | 1777 | 1816 | Public Domain | Public Domain | Public Domain | **CLEARED (Global Public Domain)** |
| **CASE A** | *The Great Gatsby* | F. Scott Fitzgerald | 1925 | 1940 | Public Domain | Public Domain | Public Domain | **CLEARED (Global Public Domain)** |
| **CASE B** | *A Passage to India* | E. M. Forster | 1924 | **1970** | Public Domain (1924) | **PROTECTED until 2031** | **PROTECTED until 2041** | **REJECTED (Protected in IN & UK/EU)** |
| **CASE C** | *The Waste Land* | T. S. Eliot | 1922 | **1965** | Public Domain (1922) | **Public Domain (Jan 2026)** | **PROTECTED until 2036** | **CONDITIONAL (US/IN only; Banned in UK/EU)** |

*Case Analysis*:
- **Case B (E. M. Forster)** illustrates the fatal flaw of relying solely on the US pre-1928 publication rule. Published in 1924 (US public domain), Forster lived until 1970. Under Section 22 of the Indian Copyright Act, it remains protected in India until January 1, 2031!
- **Case C (T. S. Eliot)** illustrates the exact difference between India and UK/EU. Eliot died in 1965. In India (Life+60), it entered the public domain on January 1, 2026. In the UK/EU (Life+70), it remains protected until January 1, 2036!

---

## 6. Audit Conclusion & Human Governance Rule

1. **Gate Status**: **`LOCKED`**. No Gutenberg text files have been downloaded or ingested.
2. **Review Requirement**: Before any Gutenberg corpus can be downloaded or evaluated, the `LEGAL_GOVERNANCE` officer and `DATA_CUSTODIAN` must complete and sign an `ITEM_LEVEL_CLEARANCE_REGISTER.csv` verifying vital dates and trademark excision for every single EBook.
