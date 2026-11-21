# IGRIS Legal Analysis: Indian Copyright Law & Statutory Term Review

**Document Version:** 2.0.0  
**Milestone:** 3C.8 — Legal Jurisdiction Correction & Pipeline Authorization Audit  
**Governing Statute:** The Copyright Act, 1957 (Act No. 14 of 1957, Government of India)  
**Target Scope:** Legal compliance for Indian language and public domain corpora  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)  
**Acquisition Status:** `NOT AUTHORIZED`  
**Human Approvals Status:** `PENDING` (Unsigned — Never Fabricate Signatures)

---

## 1. Executive Summary & Statutory Correction

In Milestone 3C.7, preliminary documentation referenced international copyright durations and colloquially grouped India with jurisdictions following a "Life + 70" rule.

**This document formally corrects that misclassification.**

Under the statutory framework of the Republic of India, the principal governing legislation is **The Copyright Act, 1957** (as amended, including the Copyright (Amendment) Act, 2012). The general term of copyright in published literary, dramatic, musical, and artistic works is **Life of the Author plus 60 years (Life + 60)**, governed specifically by **Section 22**.

Furthermore, this review establishes that:
1. The blanket **1955 author death-year threshold** cited in Milestone 3C.7 applies to the **United Kingdom and European Union (Life + 70)**, **not to India**.
2. For calendar year **2026 in India**, the ordinary author death-year threshold under Section 22 is **1965** ($\le 1965$ has entered the public domain; $\ge 1966$ remains protected).
3. Copyright subsistence cannot be evaluated solely by the author's death date. Statutory exceptions—including **Joint Authorship (Section 22 Explanation)**, **Anonymous and Pseudonymous Works (Section 23)**, **Posthumous Works (Section 24)**, and **Government Works (Section 28)**—frequently extend protection decades beyond ordinary life calculations.
4. Old literary works cannot automatically be presumed to be in the public domain; translations, critical editions, and moral rights under Section 57 create independent legal encumbrances.

---

## 2. Statutory Provisions of The Copyright Act, 1957

### 2.1 Section 22: Ordinary Term for Published Literary Works
Section 22 provides:
> *"Except as otherwise hereinafter provided, copyright shall subsist in any literary, dramatic, musical or artistic work (other than a photograph) published within the lifetime of the author until sixty years from the beginning of the calendar year next following the year in which the author dies."*

#### Statutory Calculation Formula:
Let $Y_{\text{death}}$ be the calendar year of the author's death.
- The statutory clock begins on **January 1st of $(Y_{\text{death}} + 1)$**.
- The 60-year term runs through **December 31st of $(Y_{\text{death}} + 60)$**.
- The work enters the Indian public domain on **January 1st of $(Y_{\text{death}} + 61)$**.

$$\text{Indian Public Domain Entry Date} = \text{January 1, } (Y_{\text{death}} + 61)$$

#### Current Application for Calendar Year 2026:
- For an author who died in **1965**:
  - Clock starts: January 1, 1966.
  - 60-year term expires: December 31, 2025.
  - Public domain entry: **January 1, 2026**. $\rightarrow$ **PUBLIC DOMAIN IN INDIA**.
- For an author who died in **1966**:
  - Clock starts: January 1, 1967.
  - 60-year term expires: December 31, 2026.
  - Public domain entry: **January 1, 2027**. $\rightarrow$ **UNDER COPYRIGHT IN INDIA IN 2026**.

**Correction**: The threshold for an author's death year in India for public domain entry in 2026 is **1965**, not 1955.

---

## 3. Statutory Exceptions to Section 22

The standard Life + 60 rule applies *only* to sole-authored works published during the lifetime of the author. The Copyright Act, 1957 sets out explicit statutory exceptions:

### 3.1 Joint Authorship (Section 22 Explanation)
The Explanation to Section 22 states:
> *"In this section the reference to the author shall, in the case of a work of joint authorship, be construed as a reference to the author who dies last."*

- **Legal Impact**: If Author A died in 1940 and Co-Author B died in 1975, the work remains under copyright in India until **January 1, 2036** ($1975 + 60 = 2035$).
- **Audit Mandate**: Data custodians cannot clear a work based on the death year of the primary author alone; all co-authors must be identified, and the death year of the last surviving author governs.

### 3.2 Anonymous and Pseudonymous Works (Section 23)
Section 23(1) provides:
> *"In the case of a literary, dramatic, musical or artistic work (other than a photograph), which is published anonymously or pseudonymously, copyright shall subsist until sixty years from the beginning of the calendar year next following the year in which the work is first published."*

- **Statutory Formula**: Expiry occurs 60 years after the calendar year of **first publication**, regardless of author lifespan.
- **Section 23(1) Proviso**: If the identity of the author is disclosed before the expiry of the 60-year period, or if the pseudonym adopted leaves no doubt as to the author's true identity, copyright reverts to **Section 22 (Life + 60)**.

### 3.3 Posthumous Works (Section 24)
Section 24(1) provides:
> *"In the case of a literary, dramatic or musical work, or an adaptation thereof, in which copyright subsists at the date of the death of the author or, in the case of a work of joint authorship, at or immediately before the date of the death of the author who dies last, but which has not been published before that date, copyright shall subsist until sixty years from the beginning of the calendar year next following the year in which the work is first published or, where an adaptation of the work is published in any earlier year, from the beginning of the calendar year next following that year."*

- **Critical Trap**: If an author died in 1910, but unpublished diaries, correspondence, or manuscripts were first published in 1980, copyright in India subsists until **January 1, 2041** ($1980 + 60 = 2040$).
- **Audit Mandate**: The publication history must be verified to confirm that the text was published during the author's lifetime.

### 3.4 Government Works (Section 28)
Section 28 provides:
> *"In the case of a Government work, where Government is the first owner of the copyright therein, copyright shall subsist until sixty years from the beginning of the calendar year next following the year in which the work is first published."*

- **Legal Impact**: Unlike the UK (Crown Copyright rules) or the US (where federal works are in the public domain under 17 U.S.C. § 105), Indian Government works are **not automatically public domain**. They remain copyrighted for 60 years from publication.

### 3.5 Works of Public Undertakings and International Organisations (Section 29)
- Section 29 provides a term of 60 years from the beginning of the calendar year next following the year in which the work is first published.

---

## 4. Rejection of Blanket Public Domain Presumptions

It is legally reckless to classify older Indian or international literature as public domain without exhaustive item-level verification. The following legal principles illustrate why:

### 4.1 Independent Copyright in Translations (Section 2(d)(v) & Section 14)
- A translation is legally an "adaptation" and constitutes an original derivative literary work.
- Even if an ancient Sanskrit epic (e.g., *Mahabharata*) or classical Tamil text (e.g., *Tirukkural*, *Silappatikaram*) is thousands of years old and unquestionably in the public domain, a modern English translation published by a scholar who died in 1970 remains protected by copyright in India until **January 1, 2031** ($1970 + 60 = 2030$).

### 4.2 Critical Editions, Annotations, and Typographical Arrangement
- Scholarly editions that incorporate critical apparatus, editorial commentary, reconstructed lacunae, textual footnotes, or specialized glossaries carry distinct copyright owned by the editor or publisher.
- Ingesting a modern scholarly edition of an old text infringes the editor's and publisher's rights.

### 4.3 Author's Special Moral Rights (Section 57)
- Section 57 of the Indian Copyright Act protects the author's special moral rights:
  1. The right to claim authorship of the work (paternity right).
  2. The right to restrain or claim damages in respect of any distortion, mutilation, modification, or other derogatory act prejudicial to the author's honour or reputation (integrity right).
- **Statutory Scope & Legal Representatives**: Under Section 57(1), moral rights survive the assignment or licensing of economic copyright during the author's lifetime. Under Section 57(2) (as amended by Act 27 of 2012), these rights may be exercised post-mortem by the legal representatives of the author.
- **Clarification on Duration (Avoiding Unsupported Blanket Claims)**: While the landmark decision in *Amar Nath Sehgal v. Union of India* (2005) affirmed that moral rights exist independently of economic assignments, the dispute arose while the underlying copyright was actively subsisting. The Copyright Act, 1957 does not explicitly provide for an unqualified, perpetual moral right persisting indefinitely into eternity after the full statutory copyright term has lapsed (unlike French *droit moral perpétuel*). Therefore, blanket claims that moral rights persist in perpetuity past statutory copyright expiry lack clear statutory or appellate consensus in India. Nevertheless, prudent AI governance mandates preserving author attribution and preventing derogatory textual distortions as essential compliance practices.

---

## 5. Comparative Jurisdictional Matrix (2026 Baseline)

| Legal Parameter | India (Copyright Act, 1957) | United Kingdom & European Union | United States (17 U.S.C.) |
| :--- | :--- | :--- | :--- |
| **Governing Standard** | Life + 60 years (Section 22) | Life + 70 years | Publication Date (Pre-1928 rule) |
| **Clock Computation** | Jan 1 of year following death | Jan 1 of year following death | 95 years from publication |
| **2026 Death Year Cut-Off** | **Author died $\le 1965$** | **Author died $\le 1955$** | N/A (Publication before 1928) |
| **Divergence Zone 1** | Authors dying 1956–1965: **Public Domain** | Authors dying 1956–1965: **Protected** | Depends on publication date |
| **Divergence Zone 2** | Works published pre-1928 where author died $\ge 1966$: **Protected** | Works published pre-1928 where author died $\ge 1956$: **Protected** | **Public Domain** |
| **Posthumous Term** | 60 years from publication (Sec 24) | 70 years / 25 years publication right | 95 years from pub or 120 from creation |
| **Joint Authorship** | 60 years after death of last author | 70 years after death of last author | 70 years after death of last author |
| **Government Works** | 60 years from publication (Sec 28) | Crown Copyright: 50–125 years | Ineligible for US copyright (§ 105) |

---

## 6. Practical Implications for IGRIS Corpora

1. **Project Gutenberg Corpora (`SRC-EN-01`, `SRC-CV-06`)**:
   - Must satisfy the **strictest applicable standard** across target deployment jurisdictions.
   - For an item to be cleared globally across US, UK/EU, and India:
     - First publication must be **pre-1928** (satisfying US rule).
     - Author and translator death year must be **$\le 1955$** (satisfying UK/EU Life+70 and India Life+60).
     - Work must have been published during author's lifetime (satisfying Indian Section 24).
     - All co-authors must have died $\le 1955$ (satisfying Indian Section 22 Explanation).
2. **Indian Language Baseline Corpora (`SRC-TM-01`, `SRC-HI-01`, `SRC-OI-01` to `05`)**:
   - Sourced from AI4Bharat IndicCorp v2 under CC0-1.0.
   - Public web crawls are evaluated under Indian intermediary liability and copyright exceptions. The CC0 dedication by AI4Bharat applies to their dataset curation, but underlying content rights must be audited before model training.
3. **Current Gate Status**: **`LOCKED`**. No Indian texts have been scraped, downloaded, or staged.
