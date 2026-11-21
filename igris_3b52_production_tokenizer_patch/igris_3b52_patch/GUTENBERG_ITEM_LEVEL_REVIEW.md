# IGRIS Project Gutenberg Item-Level Public Domain & Legal Review Specification

**Document Version:** 1.0.0  
**Status:** Mandatory Legal Compliance Protocol (Milestone 3C.7)  
**Governing Standard:** IGRIS Legal & Governance Framework  
**Target Corpora:** `SRC-EN-01` (Project Gutenberg Open Archive), `SRC-CV-06` (Project Gutenberg Theatrical Dialogue)  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)  
**Corpus Ingestion Status:** `NOT AUTHORIZED`  
**Human Approvals Status:** `PENDING` (Unsigned — Never Fabricate Signatures)

---

## 1. Executive Summary & Critical Legal Mandate

Project Gutenberg is a premier global repository of free electronic books. However, a widespread misconception in machine learning engineering is that text sourced from Project Gutenberg is "unconditionally in the public domain worldwide and carries zero legal risk."

**This claim is legally invalid and rejected by IGRIS governance.**

The Project Gutenberg Literary Archive Foundation (PGLAF) operates primarily under **United States copyright law**. A book that is legally in the public domain in the United States may still be fully protected by copyright in other major jurisdictions—specifically the United Kingdom, the European Union, and India—due to differing copyright terms.

Furthermore, the phrase **"Project Gutenberg" is a registered trademark**, and PGLAF's Terms of Use impose strict header/footer removal requirements prior to any redistribution, fine-tuning, or commercial model deployment.

> [!CAUTION]
> **GOVERNANCE DIRECTIVE**:
> 1. Never claim "zero copyright risk globally" for Project Gutenberg corpora.
> 2. Under no circumstances may raw bulk Gutenberg text be ingested without an item-level public domain review.
> 3. All Project Gutenberg headers, footers, license texts, and trademarks must be programmatically excised prior to any corpus staging.

---

## 2. Cross-Jurisdictional Copyright Term Discrepancies

### 2.1 United States Law (Publication Date Rule)
- Under US copyright law (Copyright Term Extension Act), works published **before 1928** are in the public domain regardless of when the author died.
- For works published between 1928 and 1977, copyright protection lasts 95 years from the date of publication (provided renewal formalities were satisfied).
- Consequently, US public domain determination is predominantly **publication-date driven**.

### 2.2 United Kingdom, European Union, and International Law (Life + 70 Rule)
- The Berne Convention and domestic statutes in the UK and European Union member states calculate copyright duration based on the **author's life plus 70 years** (Life + 70), expiring on December 31st of the 70th year following the author's death.
- In India, under Section 22 of the Copyright Act, 1957, the general copyright term for literary works is the life of the author plus **60 years** from the beginning of the calendar year following the author's death (Life + 60), while certain foreign reciprocal treaties recognize Life + 70.
- **The Divergence**: If an author published a play in 1925 (pre-1928, US public domain) but died in 1965:
  - In the **United States**: The work is in the public domain.
  - In the **UK / EU**: The work remains protected by copyright until **January 1, 2036** ($1965 + 70 = 2035$).
  - In **India**: The work remains protected until **January 1, 2026** ($1965 + 60 = 2025$).
- In 2026, any author who died **after 1955** remains under copyright in jurisdictions with a Life + 70 rule. Distributing a model trained on such works in the UK or EU would constitute global copyright infringement.

### 2.3 Jurisdictional Comparison Matrix

| Legal Parameter | United States | United Kingdom & European Union | India (Copyright Act, 1957) |
| :--- | :--- | :--- | :--- |
| **Primary Standard** | Date of Publication (Pre-1928 rule) | Life of author + 70 years | Life of author + 60 years |
| **Current Cut-Off (2026)** | Works published before 1928 | Author died before January 1, 1956 | Author died before January 1, 1966 |
| **High-Risk Conflict Zone** | Works published 1900–1927 by authors who lived past 1955 | **Protected by copyright** | **Protected if author lived past 1965** |
| **IGRIS Release Policy** | Global deployment requires meeting the **strictest jurisdictional standard** (Author death $\le 1955$). |

---

## 3. Project Gutenberg Trademark & Header Removal Mandate

### 3.1 Trademark Protection
"Project Gutenberg" is a registered trademark owned by the Project Gutenberg Literary Archive Foundation (PGLAF). The trademark does not expire with public domain text.

### 3.2 PGLAF License Paragraph 1.E Requirements
Under Paragraph 1.E.1 of the standard Project Gutenberg license:
> *"If an individual Project Gutenberg electronic work is derived from texts not protected by U.S. copyright law (does not contain a notice indicating that it is posted with permission of the copyright holder), the work can be copied and distributed to anyone in the United States without paying any fees or charges. If you are redistributing or providing access to a work with the phrase 'Project Gutenberg' associated with or appearing on the work, you must comply either with the requirements of paragraphs 1.E.1 through 1.E.7 or obtain permission for the use of the work and the Project Gutenberg trademark..."*

Paragraph 1.E.8 states:
> *"You may use this eBook for nearly any purpose such as creation of derivative works, reports, performances and research. They may be modified and printed and given away—you may do practically ANYTHING in the United States with eBooks not protected by U.S. copyright law. Redistribution is subject to the trademark license, especially commercial redistribution."*

### 3.3 Mandatory Pre-Processing Sanitization Protocol
Before any text file from `SRC-EN-01` or `SRC-CV-06` may be converted to tokens or staged for evaluation:
1. **Header Stripping**: Programmatically identify and strip all front matter preceding the official marker:
   `*** START OF THE PROJECT GUTENBERG EBOOK <TITLE> ***`
2. **Footer Stripping**: Programmatically identify and strip all end matter starting from the official marker:
   `*** END OF THE PROJECT GUTENBERG EBOOK <TITLE> ***`
3. **Trademark Scrubbing**: Perform a regex sweep (`(?i)project\s+gutenberg`) across all text to ensure no residual PGLAF disclaimers, solicitation notices, or trademark references remain.

---

## 4. Item-Level Review Protocol (Mandatory Checklist)

Before any individual text item from `SRC-EN-01` or `SRC-CV-06` is admitted to the authorized dataset manifest, the Data Custodian and Legal Governance officers must complete the following 6-step verification:

```
+----------------------------------------------------------------------------------------------------+
|                         GUTENBERG ITEM-LEVEL REVIEW WORKFLOW                                       |
+----------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
                     [Step 1: Record Metadata (Title, Author, Pub Date)]
                                                  |
                                                  v
                     [Step 2: Check US Public Domain Status (Pub < 1928)]
                                                  |
                     +----------------------------+----------------------------+
                     | No                                                      | Yes
                     v                                                         v
             [REJECT: US Protected]                         [Step 3: Check Author Death Date]
                                                                               |
                                                  +----------------------------+----------------------------+
                                                  | Death > 1955                                            | Death <= 1955
                                                  v                                                         v
                                       [REJECT: UK/EU/IN Protected]                       [Step 4: Check Translation Rights]
                                                                                                            |
                                                                                +---------------------------+---------------------------+
                                                                                | Translator Death > 1955                               | Translator Death <= 1955
                                                                                v                                                       v
                                                                     [REJECT: Translation Protected]                     [Step 5: Verify Header & Trademark Removal]
                                                                                                                                                |
                                                                                                                                                v
                                                                                                                             [Step 6: Issue Cryptographic Item Hash]
                                                                                                                                                |
                                                                                                                                                v
                                                                                                                                 [APPROVED FOR INGESTION]
```

### Protocol Fields:
1. **Item Identifier**: Gutenberg EBook Number (e.g., `#1524`, `#100`).
2. **Author Full Name & Vital Dates**: Birth year and death year verified against authoritative bibliographies (Library of Congress / VIAF).
3. **Primary Publication Year**: Year of first public release. Must be prior to 1928.
4. **Author Death Year Verification**: Author death year must be **$\le 1955$** (satisfying US, UK, EU, and India Life+70 requirements).
5. **Translator / Editor Check**: If the work is a translation (e.g., Constance Garnett translating Tolstoy, or Alexander Pope translating Homer), the translator's death date must **also** be $\le 1955$.
6. **Trademark Excision Verification**: Checksum of text computed strictly on the clean body text post-header/footer removal.

---

## 5. Sample Audit of Candidate Dramatic Works (`SRC-CV-06`)

To demonstrate the strict application of this policy, five candidate theatrical works considered for Category 9 (`SRC-CV-06`) were evaluated against the item-level criteria:

| EBook ID | Work Title | Author | First Pub Year | Author Death Year | US Status | UK / EU Status (Life+70) | India Status (Life+60) | Item Clearance Verdict |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **#1524** | *Hamlet* | William Shakespeare | 1603 | 1616 | Public Domain | Public Domain | Public Domain | **CLEAR (Global Public Domain)** |
| **#844** | *The Importance of Being Earnest* | Oscar Wilde | 1895 | 1900 | Public Domain | Public Domain | Public Domain | **CLEAR (Global Public Domain)** |
| **#3825** | *Pygmalion* | George Bernard Shaw | 1913 | 1950 | Public Domain | **Protected until 2021** (Now PD in 2026) | Public Domain | **CLEAR (Global Public Domain in 2026)** |
| **#1112** | *The School for Scandal* | Richard Brinsley Sheridan | 1777 | 1816 | Public Domain | Public Domain | Public Domain | **CLEAR (Global Public Domain)** |
| **#1308** | *The Playboy of the Western World* | J. M. Synge | 1907 | 1909 | Public Domain | Public Domain | Public Domain | **CLEAR (Global Public Domain)** |
| **COUNTER**| *Saint Joan* | George Bernard Shaw | 1923 | 1950 | Public Domain | PD in 2021 | PD | **CLEAR** |
| **COUNTER**| *Waiting for Godot* | Samuel Beckett | 1952 | 1989 | Protected | Protected until 2060 | Protected until 2050 | **REJECTED (Globally Protected)** |

---

## 6. Audit Enforcement & Human Approval Gate

1. **Automated Gate Check**: Any dataset manifest containing `SRC-EN-01` or `SRC-CV-06` must accompany an `ITEM_LEVEL_PUBLIC_DOMAIN_MANIFEST.csv` detailing the author death year and publication year for every text file.
2. **Human Legal Sign-off**: The `LEGAL_GOVERNANCE` officer must independently verify that:
   - No text item contains an author or translator who died after 1955.
   - PGLAF trademark notices and header/footers are 100% stripped.
   - No claim of "zero copyright risk globally" is made in any release documentation.
3. **Current Gate Status**: `LOCKED`. No Gutenberg text has been downloaded, ingested, or staged.
