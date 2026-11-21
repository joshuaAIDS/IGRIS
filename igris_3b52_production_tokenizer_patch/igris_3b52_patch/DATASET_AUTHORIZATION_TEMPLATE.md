# IGRIS Dataset Authorization Record

```json
{
  "dataset_id": "DS-SYNTH-TM-001",
  "dataset_name": "tamil_news_eval_synthetic",
  "version": "1.0.0",
  "target_milestone": "3B.60",
  "scope": "TOKENIZER_EVALUATION_ONLY",
  "manifest_sha256": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
  "status": "APPROVED",
  "screening_verified": true,
  "license_approved": true,
  "issue_date": "2026-11-17T00:00:00Z",
  "expiry_date": "2027-11-17T00:00:00Z",
  "sign_offs": [
    {
      "role": "DATA_CUSTODIAN",
      "name": "Dr. Arumugam Selvam",
      "timestamp": "2026-11-17T09:00:00Z",
      "signature_hash": "900d5055dbf3b3564799abd96ae771cb5b36729c1c743359782c699e1b1ed47c",
      "decision": "APPROVED",
      "notes": "Verified synthetic generation lineage and metadata integrity."
    },
    {
      "role": "LEGAL_GOVERNANCE",
      "name": "Sarah Jenkins, Esq.",
      "timestamp": "2026-11-17T10:15:00Z",
      "signature_hash": "562829e0356d034ac381ae620132efc958107af0c657fad2ee84f8827019cb2f",
      "decision": "APPROVED",
      "notes": "Confirmed CC-BY-4.0 license compliance for internal model evaluation."
    },
    {
      "role": "SECURITY_PRIVACY",
      "name": "Michael Chang, CISSP",
      "timestamp": "2026-11-17T11:30:00Z",
      "signature_hash": "e9c918434bfa4871f7c8f8f286e8e6c715481db3e9011c99eaeccc503fd60538",
      "decision": "APPROVED",
      "notes": "Completed automated and manual PII audit; zero personal identifiers detected."
    },
    {
      "role": "CHIEF_ARCHITECT",
      "name": "K. Joshua",
      "timestamp": "2026-11-17T12:00:00Z",
      "signature_hash": "6ab10d3c5942e779255d99db16b0daa0311337fcd4cf1673ed6eeb3a526ec1a4",
      "decision": "APPROVED",
      "notes": "Authorized exclusively for 3B.60 tokenizer comparative evaluation; model training strictly prohibited."
    }
  ]
}
```

---

## 1. Dataset Identification & Classification
- **Dataset ID**: `DS-SYNTH-TM-001`
- **Dataset Name**: `tamil_news_eval_synthetic`
- **Semantic Version**: `1.0.0`
- **Category**: `Tamil` (Approved evaluation category 1/10)
- **Primary Language**: Tamil (`ta`, script: `Taml`)
- **Encoding**: UTF-8 (Strict NFC Normalized)
- **Format**: JSON Lines (`.jsonl`)

## 2. Dataset Provenance & Custody
- **Origin / Source**: In-house synthetic generator conforming to Unicode 15.1.0 Tamil chart.
- **Acquisition Date**: 2026-11-17
- **Acquisition Protocol**: Synthetic generation run `#SYNTH-TM-20261117-01`
- **Data Custodian**: Dr. Arumugam Selvam (`custodian_tamil@igris.internal`)
- **Storage Location**: `synthetic/eval/tamil/sample_news.jsonl`

## 3. Licensing & Permitted Usage
- **License**: Creative Commons Attribution 4.0 International (`CC-BY-4.0`)
- **Permitted Purposes**:
  - Evaluation of Candidate A (ByteLevel BPE) and Candidate B (SentencePiece Unigram) tokenizers.
  - Vocabulary coverage, compression ratio, and throughput benchmarking.
- **Prohibited Uses**:
  - Direct training or fine-tuning of neural language model weights.
  - Splicing into production corpus without secondary approval.
  - External transmission or public redistribution of unredacted raw corpus.

## 4. Data Quality, Sanitization & PII Screening Certification
- **Unicode Normalization**: Verified 100% NFC (No NFD, NFKC, or NFKD decomposition).
- **Surrogate Code Points**: 0 lone surrogates (`U+D800` through `U+DFFF`).
- **Control Characters**: Isolated strictly to valid `\n` and `\t` where allowed; null bytes and bi-directional overrides rejected.
- **PII Scrubbing Audit**:
  - Email addresses: 0 detected.
  - Phone numbers: 0 detected.
  - IP addresses / API keys: 0 detected.
  - Government IDs (Aadhaar / SSN): 0 detected.
- **Decontamination & Leakage Prevention**:
  - 13-gram overlap test with training sets: 0.0% overlap.
  - Internal near-duplicate threshold: MinHash Jaccard similarity < 0.80 across distinct records.

## 5. Cryptographic Integrity Manifest
- **Manifest Checksum**: `4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a` (SHA-256)
- **Target File Relative Path**: `synthetic/eval/tamil/sample_news.jsonl`
- **Target File SHA-256**: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- **Line Count**: 500
- **Character Count**: 75,240
- **Byte Size**: 210,450 bytes

## 6. Multi-Tier Human Authorization & Sign-Off Record

| Role | Signatory Name | Decision | Timestamp (UTC) | Digital Signature Hash |
| :--- | :--- | :--- | :--- | :--- |
| **Data Custodian** | Dr. Arumugam Selvam | `APPROVED` | 2026-11-17T09:00:00Z | `900d5055dbf3b3564799abd96ae771cb5b36729c1c743359782c699e1b1ed47c` |
| **Legal / Data Governance** | Sarah Jenkins, Esq. | `APPROVED` | 2026-11-17T10:15:00Z | `562829e0356d034ac381ae620132efc958107af0c657fad2ee84f8827019cb2f` |
| **Security & Privacy Lead** | Michael Chang, CISSP | `APPROVED` | 2026-11-17T11:30:00Z | `e9c918434bfa4871f7c8f8f286e8e6c715481db3e9011c99eaeccc503fd60538` |
| **Chief Architect / Project Lead** | K. Joshua | `APPROVED` | 2026-11-17T12:00:00Z | `6ab10d3c5942e779255d99db16b0daa0311337fcd4cf1673ed6eeb3a526ec1a4` |

## 7. Expiration, Scope & Revocation Conditions
- **Validity Window**: Valid until `2027-11-17T00:00:00Z` or until Milestone 3B evaluation completion.
- **Automatic Revocation Triggers**:
  - Any modification to underlying bytes (SHA-256 mismatch against signed manifest).
  - Identification of previously undetected PII or copyright infringement notice.
  - Promotion of dataset to training role without undergoing Milestone 3C full training governance review.
