# PHASE 22B — STORAGE LIFECYCLE RECONCILIATION & HIGH-WATER PROOF
## Rigorous Component Equations, Architectural Code Path Verification, and 1 TB Provisioning Safety Proof

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 22B  
**Status:** FULLY RECONCILED  

---

## 1. Executive Summary

Phase 22B investigates and resolves every component-level equation underlying the IGRIS storage lifecycle.

### Core Architectural Proofs Established:
1. **Single-Copy Quarantine Code Path Proven:**
   - Inspection of `scripts/secure_acquisition_engine.py` (lines 348–349, 426–485) proves that the acquisition engine writes directly to `<destination_path>.part` and atomically renames to `<destination_path>` inside quarantine.
   - There is **no separate external download directory**.
   - Therefore, the claimed single-copy lifecycle (183.70 GB, not $183.70 	imes 2 = 367.40	ext{ GB}$) is substantiated directly by the codebase.
2. **The 393.70 GB Sequential Peak Equation Fully Explained:**
   - The sequential high-water mark occurs exclusively during **Stage 2 (Cleaning & Deduplication)** when raw text, cleaned text, MinHash index tables, intermediate sorting scratch, and OS headroom reserve must coexist simultaneously:
     $$\begin{aligned}
     \text{Sequential Peak} &= \text{Raw Corpus (183.70 GB)} + \text{Cleaned Text (130.00 GB)} + \text{MinHash Dedup Index (10.00 GB)} \\
     &\quad + \text{Intermediate Scratch (20.00 GB)} + \text{OS Headroom Reserve (50.00 GB)} \\
     &= \mathbf{393.70\text{ GB decimal (366.66 GiB binary)}}.
     \end{aligned}$$
   - Treating OS headroom separately:
     $$\text{Application Data Footprint} = 183.70 + 130.00 + 10.00 + 20.00 = \mathbf{343.70\text{ GB (320.09 GiB)}}.$$
     $$\text{Total System Peak} = 343.70 + 50.00 = \mathbf{393.70\text{ GB (366.66 GiB)}}.$$
3. **Corrected Shard Streaming Buffer (26.70 GB vs. 26.30 GB):**
   - Phase 22A budgeted 26.30 GB based on `data/ml.txt`. However, the largest single IndicCorp v2 shards are the Hindi shards (`data/hi-1.txt`, `data/hi-2.txt`, `data/hi-3.txt`), which are each **26.70 GB (24.87 GiB)**.
   - Adjusting the transient buffer to **26.70 GB** yields:
     - Minimum Theoretical Capacity: **260.40 GB decimal (242.52 GiB binary)**.
     - In-Place Simultaneous Peak (zero intermediate deletion): **447.40 GB decimal (416.67 GiB binary)**.
     - Conservative Duplicate-Copy Peak: **631.10 GB decimal (587.76 GiB binary)**.
4. **Proof of 1 TB Provisioning Sufficiency:**
   - A standard 1 TB cloud volume ($1,000.00	ext{ GB decimal} = 931.32	ext{ GiB binary}$) is **fully sufficient even under the most conservative duplicate-copy zero-cleanup scenario** ($631.10\text{ GB} \le 1,000.00\text{ GB}$, leaving **368.90 GB (343.56 GiB)** of unallocated headroom).
   - Under standard sequential execution with verified cleanup, peak usage is 393.70 GB, leaving **606.30 GB (564.66 GiB)** of free headroom.

---

## 2. Code Path Verification: Single-Copy Quarantine Ingress

Inspection of `scripts/secure_acquisition_engine.py`:
```python
# Lines 348-349
dest_path = Path(destination_path)
part_path = Path(str(destination_path) + ".part")

# Lines 431-464: Stream directly into destination directory as .part
with open(part_path, "wb") as part_file:
    ...
    sha256_hasher.update(chunk)
    part_file.write(chunk)

# Lines 481-483: Atomic promotion in place
part_path.replace(dest_path)
```
- When `destination_path` is passed as `quarantine/incoming/ta.txt`, the stream writes directly to `quarantine/incoming/ta.txt.part` and renames to `quarantine/incoming/ta.txt`.
- No secondary or temporary external copy is spawned.
- The dual-copy assumption ($183.70 + 183.70 = 367.40	ext{ GB}$) is purely an artifact of conservative external staging assumptions and is not required by IGRIS infrastructure.

---

## 3. Five-Stage Sequential High-Water Profile

```
+----+----------------------+-------------------------------------------------------+-----------+-----------+-----------------------+
| Stg| Processing Stage     | Active Components Co-existing Simultaneously          | App (GB)  | Total(GB) | Post-Stage Cleanup    |
+----+----------------------+-------------------------------------------------------+-----------+-----------+-----------------------+
| 1  | Ingress & Validation | Raw in Quarantine (183.70) + Shard Buffer (26.70)     | 210.40 GB | 260.40 GB | Purge buffer (-26.70) |
| 2  | Clean & Deduplicate  | Raw (183.70) + Clean (130.00) + Dedup (10) + Scratch  | 343.70 GB | 393.70 GB | Purge raw & dedup     |
| 3  | Tokenization         | Cleaned Text (130.00) + Tokens (12.00) + Scratch (20) | 162.00 GB | 212.00 GB | Purge cleaned text    |
| 4  | Pretraining          | Tokens (12.00) + Checkpoints (15.00) + Logs (10.00)   | 37.00 GB  | 87.00 GB  | Rolling ckpt purge    |
+----+----------------------+-------------------------------------------------------+-----------+-----------+-----------------------+
|    | SEQUENTIAL PEAK      | Maximum at Stage 2 (Cleaning & Deduplication)         | 343.70 GB | 393.70 GB | Mandatory Peak Target |
+----+----------------------+-------------------------------------------------------+-----------+-----------+-----------------------+
```
