# PHASE 29A — EVIDENCE CORRECTION AUDIT REPORT

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-20  
**Phase:** Phase 29A (Forensic Evidence Correction Audit)  
**Mode:** READ-ONLY EVIDENCE CORRECTION (Zero Production Ingress Authorized)

---

## 1. Executive Summary & Purpose

Phase 29A conducts a rigorous forensic audit of the individual dataset review packages produced in Phase 29 prior to any source-level owner decisions.

The objective is to eliminate overgeneralized legal assertions, correct misinterpretations of primary license terms, replace absolute privacy claims with evidence-qualified realities, and mark unsupported assumptions as **`UNVERIFIED`**.

### Summary of Major Corrections:
1. **Project Gutenberg (`SRC-EN-01`, `SRC-CV-06`):**
   - Corrected the misinterpretation that Section 1.E.8 "universally mandates stripping".
   - Clarified the distinction between disclaiming the PGLAF license (by stripping headers) and complying with trademark/royalty provisions (paying 20% royalties under § 1.E.8).
   - Replaced catalog-wide public domain assumptions with item-level copyright notice verification requirements.
   - Reclassified the `author_death_year <= 1955` filter as a *preliminary screening heuristic*, not a formal global legal clearance.
2. **IETF RFC Repository (`SRC-TD-02`):**
   - Replaced the claim of "uniform permissive licensing" across all RFCs with an accurate audit of IETF Trust Legal Provisions (TLP 5.0 Section 3, 4, 5, 6).
   - Documented the "pre-RFC 5378 problem" (RFCs published prior to November 10, 2008 under RFC 2026 / RFC 3978), Independent Submission Stream variations, and embedded third-party specifications (MIBs, vendor protocols).
3. **MultiWOZ 2.4 English (`SRC-CV-05`):**
   - Corrected the false assertion that all entities are "synthetic". Audited the Cambridge database to reveal **real Cambridge venue names, real addresses, real phone numbers, and real postcodes** (e.g. Gonville Hotel, Lensfield Hotel, CB2 1SJ).
   - Audited the repository licensing vs. data licensing split, identifying that the GitHub repository license applies to code, while underlying dialogue data provenance retains academic research constraints.
   - Noted `OWNER_REQUIRES_MORE_EVIDENCE` as a viable future owner review direction.
4. **Privacy Claims (All Six Candidates):**
   - Completely abolished absolute declarations (`ZERO REAL PII`, `ZERO LIVING PII`, `NO PERSONAL INFORMATION`).
   - Qualified all privacy statements based on detection methodologies, volunteer transcriber notices in Gutenberg, developer acknowledgments in Python docs, and real engineer contact details in RFCs.
5. **Preservation of Owner Governance:**
   - All six owner review candidates remain strictly initialized to **`NOT_REVIEWED`**. Zero decisions populated.

---

## 2. Forensic Correction Section 1: Project Gutenberg Terms

### A. Misinterpretation in Phase 28/29
Previous packages stated: *"PGLAF License Section 1.E.8 universally mandates removal of all Project Gutenberg references, headers, and footers."*

### B. Correct Legal Interpretation of PGLAF Terms
The official Project Gutenberg license operates on a dual-track structure:
* **Track 1: Retaining the Project Gutenberg Trademark (§ 1.C, § 1.D, § 1.E):**
  - If a distributor retains the "Project Gutenberg" trademark and license headers:
    - Non-commercial distribution is permitted without fee under § 1.C.
    - If any fee is charged, or if a commercial product or service is created, **Section 1.E.8 mandates that 20% of net profits must be paid as a royalty to PGLAF**, or a separate written trademark contract must be executed.
* **Track 2: Disclaiming the PGLAF License & Stripping Trademarks (§ 1.C, § 1.E.8):**
  - Section 1.E.8 provides: *"If you do not charge anything for copies of this eBook, complying with the rules is very easy... If you wish to charge a fee or distribute a Project Gutenberg-tm electronic work or group of works on different terms... you must remove all references to Project Gutenberg: 1.E.8. You may convert to binary, compressed, marked up, nonproprietary or proprietary form... You may charge a reasonable fee... provided that you remove all references to Project Gutenberg."*
  - **Correction:** Stripping is **not** a universal statutory mandate; it is an *elective disclaimer mechanism*. Stripping trademark notices allows a downstream user to disclaim the PGLAF contract entirely and rely strictly on public domain copyright law for the underlying text.

### C. Individual Work Copyright Status
* Project Gutenberg contains ~70,000 titles. While the vast majority are pre-1929 US public domain works, **some works are copyrighted titles distributed with express permission from living authors or estates**.
* Furthermore, translations and modern critical editions published after 1928 hold independent copyright in the translation or introductory apparatus, even if the ancient author died millennia ago (e.g. Homer translated in 1950).
* **Correction:** Catalog inclusion does not guarantee public domain status. Each title requires item-level copyright notice parsing.

### D. Author Death Year Screening vs. Legal Clearance
* The `author_death_year <= 1955` filter (70+ years post-mortem as of 2026) is a **preliminary technical heuristic**.
* It does not constitute formal legal clearance because:
  1. Joint authors: The term is measured from the death of the *longest-living author*.
  2. Corporate works or works made for hire: Term may be 95 years from publication or 120 years from creation.
  3. Translators and illustrators: Hold separate copyrights.
  4. Jurisdictional differences: Project deployment in India (Life+60) vs EU/UK (Life+70) vs US (publication date pre-1929) requires jurisdiction-specific conflict-of-laws analysis.

---

## 3. Forensic Correction Section 2: IETF RFC Rights & Stream Variations

### A. Misinterpretation in Phase 28/29
Previous packages characterized the entire RFC repository as having a uniform, permissive grant under IETF TLP 5.0 § 3.c.

### B. Correct Legal Interpretation of IETF Rights
1. **Four Distinct Publication Streams:**
   - RFCs are published via four distinct streams with differing copyright assignments:
     * *IETF Stream:* Standards track; full IETF consensus.
     * *IAB Stream:* Internet Architecture Board.
     * *IRTF Stream:* Internet Research Task Force (research specifications).
     * *Independent Submission Stream (ISE):* Submissions outside the IETF process.
2. **The Pre-RFC 5378 Problem (Legacy RFCs):**
   - RFC 5378 was adopted on November 10, 2008.
   - RFCs published prior to November 10, 2008 (RFC 1 through approximately RFC 5377) were contributed under older regimes (RFC 2026 / RFC 3978), where authors did **not** grant the IETF Trust broad derivative work rights.
   - While the IETF Trust adopted TLP Section 6.c to address legacy RFCs, third-party rights holders from the 1980s and 1990s never executed retroactive assignments.
3. **Embedded Third-Party Content & Code:**
   - RFCs frequently include MIB (Management Information Base) definitions, ASN.1 modules, XML schemas, and reference C/Python code.
   - Certain RFCs contain explicit copyright notices reserving rights or restricting derivative modifications (e.g. cryptographic specifications submitted by corporations).
   - **Correction:** The RFC repository cannot be treated as a monolithic, uniformly cleared permissive corpus. A stream-aware and header-aware license parser is mandatory.

---

## 4. Forensic Correction Section 3: MultiWOZ 2.4 Provenance & Entity Reality

### A. Misinterpretation in Phase 28/29
Previous packages asserted: *"Zero real PII. All dialogue entities (hotels, restaurants, phone numbers, addresses, postcodes) are drawn from a synthetic mock database of Cambridge services."*

### B. Correct Forensic Audit of MultiWOZ Entities
Inspection of the actual MultiWOZ database files (`restaurant_db.json`, `hotel_db.json`, `attraction_db.json`) reveals:
* **Real Commercial Business Names:** "The Gonville Hotel", "The Cambridge Belfry", "Acorn Guest House", "Lensfield Hotel", "Grafton Hotel", "D'Arry's Cookhouse", "Pizza Hut City Centre", "Nando's Cambridge".
* **Real Physical Addresses:** Real streets in Cambridge, UK (e.g. "Gonville Place", "Lensfield Road", "Regent Street").
* **Real Postcodes:** Authentic UK postal codes (e.g. `CB2 1SJ`, `CB1 2ER`, `CB4 1HA`).
* **Real Telephone Numbers:** Actual landline telephone numbers matching Cambridge area code prefixes (`01223 ...`).
* **Synthetic Elements:** Only booking reference IDs (e.g. `7DFG987A`), simulated user names ("John", "Mary"), and conversational booking scenarios were generated by crowd workers.
* **Correction:** Labeling all MultiWOZ entities as "synthetic" was factually false. The corpus contains real business contact details, real geographic locations, and real venue information.

### C. Data License vs. Code Repository License
* The MultiWOZ 2.4 GitHub repository (`smartyfh/MultiWOZ2.4`) contains an Apache-2.0 `LICENSE` file.
* However, MultiWOZ 2.4 is a cleaned annotation layer built upon MultiWOZ 2.0 (Budzianowski et al., EMNLP 2018), which was collected via Amazon Mechanical Turk under academic research protocols.
* **Correction:** Whether the underlying crowd-worker dialogue utterances are legally licensed under Apache-2.0 or remain restricted by academic research consent terms is **UNVERIFIED**. If evidence is insufficient, `OWNER_REQUIRES_MORE_EVIDENCE` is the recommended posture for the project owner.

---

## 5. Forensic Correction Section 4: Privacy & PII Claim Corrections

### Abolition of Absolute Statements
In previous reports, claims of "zero PII" or "zero living personal information" were made without qualifying the scope of detection.

```
+-------------------+--------------------------------+--------------------------------------------------------------+
| Candidate         | Previous Overstatement         | Corrected Evidence-Based Qualification                       |
+-------------------+--------------------------------+--------------------------------------------------------------+
| SRC-EN-01         | "ZERO LIVING PII"              | Classical literature contains deceased authors, but modern   |
| (Gutenberg)       |                                | digital editions contain living volunteer proofreader names, |
|                   |                                | transcriber credits, and donor acknowledgments.             |
+-------------------+--------------------------------+--------------------------------------------------------------+
| SRC-TD-02         | "LOW RISK (BUSINESS ONLY)"     | RFC footers contain real living engineers' names, business   |
| (IETF RFCs)       |                                | emails, physical work addresses, and phone numbers.          |
+-------------------+--------------------------------+--------------------------------------------------------------+
| SRC-TD-03         | "ZERO PII RISK"                | Core developer acknowledgments, commit authors, and bug     |
| (Python Docs)     |                                | tracker contributors contain real living personal names.     |
+-------------------+--------------------------------+--------------------------------------------------------------+
| SRC-CV-03         | "MEDIUM RISK (SCRUBBED)"       | Volunteer prompters occasionally shared personal anecdotes,  |
| (OASST1 En)       |                                | social handles, and locations. Automated NER has limitations.|
+-------------------+--------------------------------+--------------------------------------------------------------+
| SRC-CV-05         | "ZERO REAL PII (SYNTHETIC)"    | FACTUALLY FALSE. Contains real Cambridge business names,     |
| (MultiWOZ 2.4)    |                                | real physical addresses, postcodes, and phone numbers.       |
+-------------------+--------------------------------+--------------------------------------------------------------+
| SRC-CV-06         | "ZERO LIVING PII"              | Classical plays feature deceased playwrights, but modern     |
| (Theatrical)      |                                | editor apparatus and PGLAF transcribers may be living.       |
+-------------------+--------------------------------+--------------------------------------------------------------+
```

> **GOVERNANCE RULE:** Automated regex and NER screening reduces exposure but **does not prove the absolute absence of personal information**. All datasets require manual sample inspection and conservative risk profiling.

---

## 6. Audit Summary of Unsupported Claims

| Source ID | Previous Claim | Audit Finding | Corrected Classification |
| :--- | :--- | :--- | :---: |
| `SRC-EN-01` | "Universal public domain across catalog" | Ebooks include modern translations & copyright-donor works | **`UNVERIFIED_PER_CATALOG_ITEM`** |
| `SRC-EN-01` | "Section 1.E.8 mandates stripping" | Stripping is an elective disclaimer mechanism | **`CORRECTED_ELECTIVE_DISCLAIMER`** |
| `SRC-TD-02` | "Uniform permissive license across RFCs" | Pre-5378 RFCs and Independent Streams have restrictions | **`UNIFORMITY_UNVERIFIED`** |
| `SRC-CV-05` | "Zero real PII (all entities synthetic)" | Database contains real Cambridge venues, phones, postcodes | **`CLAIM_REFUTED_REAL_ENTITIES`** |
| `SRC-CV-05` | "Apache-2.0 covers all dialogue data" | Repository code is Apache-2.0; data provenance ambiguous | **`DATA_LICENSE_UNVERIFIED`** |
| All | "Author death year <= 1955 = legal clearance" | Preliminary heuristic; doesn't cover joint authors/translators | **`PRELIMINARY_HEURISTIC_ONLY`** |
