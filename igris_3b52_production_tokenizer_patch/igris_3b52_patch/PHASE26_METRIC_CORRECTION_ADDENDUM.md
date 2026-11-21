# PHASE 26 — Metric Correction Addendum

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Phase:** Phase 26 Addendum (issued during Phase 27 entry)  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Date:** 2026-11-20  
**Purpose:** Formal correction of narrative metric discrepancies identified during Phase 27 entry audit  
**Methodology:** Independent recalculation from saved per-record predictions in `PHASE26_TEST_RESULTS.json`

> [!IMPORTANT]
> This addendum corrects discrepancies found in the **Phase 26 chat-session narrative** (the conversational completion report presented to the user). The **saved deliverable files** (`PHASE26_LANGUAGE_IDENTIFICATION_REPORT.md`, `PHASE26_COMPLETION_REPORT.md`, `PHASE26_TEST_RESULTS.json`) are internally consistent and contain the correct values. No historical deliverable files are modified.

---

## 1. Independent Recalculation Results

The Phase 27 entry requirement mandated independent recalculation of precision, recall, F1 and macro F1 directly from the saved held-out predictions and ground-truth labels. The recalculation was performed using `C:\IGRIS\scratch\recalculate_phase26_metrics.py`.

### A. Recalculation Verdict

**All three splits (dev, val, test) passed independent recalculation with zero discrepancies between saved per-record detail records and reported aggregate metrics.**

| Split | Records | Reported Accuracy | Recalculated Accuracy | Match |
|---|:---:|:---:|:---:|:---:|
| Development (`dev`) | 100 | 0.99 (99/100) | 0.99 (99/100) | ✓ |
| Validation (`val`) | 100 | 1.00 (100/100) | 1.00 (100/100) | ✓ |
| Held-Out Test (`test`) | 100 | 0.98 (98/100) | 0.98 (98/100) | ✓ |

### B. Held-Out Test Set — Recalculated Confusion Matrix

Recalculated directly from 100 per-record `{true, pred}` pairs:

| True \ Predicted | ENGLISH | OUT_OF_SCOPE | TAMIL | TANGLISH | UNKNOWN |
|---|:---:|:---:|:---:|:---:|:---:|
| **ENGLISH** | **26** | 0 | 0 | 0 | 0 |
| **OUT_OF_SCOPE** | 0 | **10** | 0 | 0 | 0 |
| **TAMIL** | 0 | 0 | **30** | 0 | 0 |
| **TANGLISH** | 1 | 0 | 0 | **30** | 0 |
| **UNKNOWN** | 1 | 0 | 0 | 0 | **2** |

### C. Held-Out Test Set — Recalculated Per-Class Metrics

| Class | Precision | Recall | F1 | Support |
|---|:---:|:---:|:---:|:---:|
| **ENGLISH** | 0.9286 | 1.0000 | 0.9630 | 26 |
| **OUT_OF_SCOPE** | 1.0000 | 1.0000 | 1.0000 | 10 |
| **TAMIL** | 1.0000 | 1.0000 | 1.0000 | 30 |
| **TANGLISH** | 1.0000 | 0.9677 | 0.9836 | 31 |
| **UNKNOWN** | 1.0000 | 0.6667 | 0.8000 | 3 |

Macro Precision: **0.9857** | Macro Recall: **0.9269** | Macro F1: **0.9493**

### D. Misclassified Records (2 of 100)

| Record ID | Ground Truth | Predicted | Text | Root Cause |
|---|---|---|---|---|
| `P26-TEST-0043` | `TANGLISH` | `ENGLISH` | "Kalyanathiku poitu vandhom, sapadu laaddu semma sweet, relatives ellarayum meet pannom." | Romanized Tamil with high English content; LID engine classified as English due to multiple English-origin words |
| `P26-TEST-0093` | `UNKNOWN` | `ENGLISH` | 90 consecutive "z" characters | Repeated single Latin character scored as English by script analysis; correctly caught by downstream Quality Filter as `REPEATED_CHAR_SPAM` |

---

## 2. Identified Narrative Discrepancies

The following discrepancies existed **only in the conversational narrative** (the Phase 26 completion message in the chat session), not in the saved deliverable files.

### Discrepancy A: Class Support Counts

| Class | Narrative Claimed | Actual (from saved data) | Status |
|---|:---:|:---:|:---:|
| TAMIL | 20 | **30** | **NARRATIVE ERROR** |
| ENGLISH | 26 | 26 | ✓ Correct |
| TANGLISH | 31 | 31 | ✓ Correct |
| OUT_OF_SCOPE | 18 | **10** | **NARRATIVE ERROR** |
| UNKNOWN | 5 | **3** | **NARRATIVE ERROR** |

**Root Cause:** The chat narrative appears to have cited approximate or draft support counts rather than the final generated split composition. The saved `PHASE26_TEST_RESULTS.json` has always contained the correct support values.

### Discrepancy B: Tamil Precision

| Metric | Narrative Claimed | Actual (from saved data) | Status |
|---|:---:|:---:|:---:|
| Tamil Precision | 0.9524 | **1.0000** | **NARRATIVE ERROR** |

**Root Cause:** A precision value of 0.9524 = 20/21 would arise if 1 non-Tamil record were predicted as Tamil. However, the actual confusion matrix shows zero false positives for Tamil (TP=30, FP=0), giving Precision = 1.0000.

### Discrepancy C: English Precision

| Metric | Narrative Claimed | Actual (from saved data) | Status |
|---|:---:|:---:|:---:|
| English Precision | 1.0000 | **0.9286** | **NARRATIVE ERROR** |

**Root Cause:** English precision is 26/(26+2) = 0.9286 because 2 non-English records (1 Tanglish + 1 Unknown) were misclassified as English. The narrative inverted precision and recall for English.

### Discrepancy D: Confusion Matrix Error Direction

| Error | Narrative Claimed | Actual (from saved data) | Status |
|---|---|---|---|
| Tanglish misclassification target | TANGLISH → TAMIL | **TANGLISH → ENGLISH** | **NARRATIVE ERROR** |

**Root Cause:** The narrative claimed one Tanglish record was misclassified as Tamil. The actual saved prediction for `P26-TEST-0043` shows `pred=ENGLISH`.

### Discrepancy E: Misclassified Record ID

| Attribute | LID Report Claimed | Actual (from saved data) | Status |
|---|---|---|---|
| Misclassified Tanglish record | P26-TEST-0046 | **P26-TEST-0043** | **NARRATIVE ERROR** |

**Root Cause:** The `PHASE26_LANGUAGE_IDENTIFICATION_REPORT.md` narrative section 5 (line 59) references `P26-TEST-0046`, but the actual misclassified record per saved predictions is `P26-TEST-0043`. Record `P26-TEST-0046` was correctly classified (pred=TANGLISH, conf=0.8).

> [!WARNING]
> This is a discrepancy in the **saved deliverable** `PHASE26_LANGUAGE_IDENTIFICATION_REPORT.md`, not just the chat narrative. The report's section 5 incorrectly identifies the misclassified record as `P26-TEST-0046` instead of `P26-TEST-0043`.

---

## 3. Corrected Authoritative Values

The following are the **verified, recalculated** held-out test set metrics:

```
Held-Out Test Set (N=100):
  Overall Accuracy:   0.98 (98/100)
  Macro Precision:    0.9857
  Macro Recall:       0.9269
  Macro F1:           0.9493
  
  Per-Class:
    TAMIL:        P=1.0000  R=1.0000  F1=1.0000  Support=30
    ENGLISH:      P=0.9286  R=1.0000  F1=0.9630  Support=26
    TANGLISH:     P=1.0000  R=0.9677  F1=0.9836  Support=31
    OUT_OF_SCOPE: P=1.0000  R=1.0000  F1=1.0000  Support=10
    UNKNOWN:      P=1.0000  R=0.6667  F1=0.8000  Support=3
    
  Misclassified:
    P26-TEST-0043: true=TANGLISH pred=ENGLISH (Romanized Tamil)
    P26-TEST-0093: true=UNKNOWN  pred=ENGLISH (90x 'z' spam)
```

---

## 4. Impact Assessment

| Impact Area | Assessment |
|---|---|
| **Saved deliverable accuracy (`PHASE26_TEST_RESULTS.json`)** | ✅ Correct — all metrics match recalculation |
| **Saved deliverable accuracy (`PHASE26_COMPLETION_REPORT.md`)** | ✅ Correct — cites 98%, 0.9493 F1 |
| **Saved deliverable narrative (`PHASE26_LANGUAGE_IDENTIFICATION_REPORT.md`)** | ⚠️ Section 5 misidentifies record P26-TEST-0046 instead of P26-TEST-0043 |
| **Chat session narrative** | ❌ Contains 5 numerical discrepancies in support counts, precision values, and confusion matrix error direction |
| **Phase 26 Verdict** | ✅ Unchanged — Verdict A remains valid; overall accuracy, macro F1, and all pass/fail conclusions are unaffected |
| **Tokenizer comparison** | ✅ Unaffected — independent of LID metrics |
| **Quality filter / duplicate detection** | ✅ Unaffected — 100% accuracy on held-out test set confirmed |

---

## 5. Recalculation Script

Independent recalculation was performed by: [`recalculate_phase26_metrics.py`](file:///C:/IGRIS/scratch/recalculate_phase26_metrics.py)

The script reads every per-record `{id, true, pred, correct, conf, diff}` detail from `PHASE26_TEST_RESULTS.json`, rebuilds the confusion matrix from scratch, recalculates per-class precision/recall/F1, computes macro averages, verifies `correct` flags match `true == pred`, and compares all values against the reported aggregates.

**Recalculation exit code: 0 (zero discrepancies between saved details and saved aggregate metrics).**

---

## 6. Conclusion

The Phase 26 machine-readable data (`PHASE26_TEST_RESULTS.json`) and the core deliverable reports (`PHASE26_COMPLETION_REPORT.md`) are internally consistent and mathematically correct. The discrepancies were confined to:

1. The conversational narrative presented in the chat session (5 errors in support counts, precision values, and confusion matrix direction).
2. One record ID error in `PHASE26_LANGUAGE_IDENTIFICATION_REPORT.md` section 5 (P26-TEST-0046 → P26-TEST-0043).

This addendum serves as the permanent correction record. Historical deliverables are preserved unmodified.
