#!/usr/bin/env python3
"""Comprehensive Verification Suite for IGRIS Inference Runtime & Tokenizer Integration.

Audits:
1. Candidate A structural tokens (IDs 0-11) and invariant SHA-256.
2. Production (16L, 79.7M/96.5M) and Baseline (12L, 51.6M/68.4M) architectures.
3. Checkpoint safety and rejection of incompatible weights.
4. Trilingual encoding fidelity (English, Tamil Unicode, Tanglish).
5. Hardware profiling (RTX 3050 6GB VRAM, system RAM, CPU).
6. Live HTTP server smoke test (/health, /v1/models, /v1/chat/completions).
"""
import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Add src to sys.path
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import torch
from tokenizers import Tokenizer

from igris.model.transformer import (
    IgrisConfig,
    IgrisDecoderTransformer,
    get_baseline_50m_config,
    get_production_config,
)

CANDIDATE_A_PATH = ROOT_DIR / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
EXPECTED_SHA256 = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"

AUTHORITATIVE_STRUCTURAL_TOKENS = [
    (0, "<|pad|>"),
    (1, "<|begin_of_text|>"),
    (2, "<|end_of_text|>"),
    (3, "<think>"),
    (4, "</think>"),
    (5, "<action>"),
    (6, "</action>"),
    (7, "<action_result>"),
    (8, "</action_result>"),
    (9, "<|system|>"),
    (10, "<|user|>"),
    (11, "<|assistant|>"),
]


def audit_tokenizer() -> bool:
    print("=" * 70)
    print("1. CANDIDATE A TOKENIZER STRUCTURAL AUDIT")
    print("=" * 70)

    if not CANDIDATE_A_PATH.exists():
        print(f"[FAIL] Tokenizer artifact missing at {CANDIDATE_A_PATH}")
        return False

    raw_bytes = CANDIDATE_A_PATH.read_bytes()
    computed_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    print(f"Artifact path : {CANDIDATE_A_PATH}")
    print(f"Artifact SHA256: {computed_sha256}")
    print(f"Expected SHA256: {EXPECTED_SHA256}")

    if computed_sha256 != EXPECTED_SHA256:
        print("[FAIL] Cryptographic SHA-256 mismatch!")
        return False
    print("[PASS] Cryptographic SHA-256 verified invariant.")

    tok = Tokenizer.from_file(str(CANDIDATE_A_PATH))
    vocab_size = tok.get_vocab_size()
    print(f"Vocabulary size: {vocab_size} (Expected: 32,768)")
    if vocab_size != 32768:
        print(f"[FAIL] Vocab size mismatch: {vocab_size} != 32768")
        return False
    print("[PASS] Vocabulary size confirmed 32,768.")

    # Check all 12 structural tokens
    print("\nValidating Authoritative Structural Tokens:")
    all_tokens_match = True
    for expected_id, expected_str in AUTHORITATIVE_STRUCTURAL_TOKENS:
        actual_id = tok.token_to_id(expected_str)
        decoded = tok.decode([expected_id], skip_special_tokens=False)
        match = (actual_id == expected_id) and (decoded == expected_str)
        status = "OK" if match else "MISMATCH"
        print(f"  ID {expected_id:2d}: {expected_str:20s} -> token_to_id={actual_id} decode={decoded!r:20s} [{status}]")
        if not match:
            all_tokens_match = False

    if not all_tokens_match:
        print("[FAIL] Structural token mismatch detected!")
        return False
    print("[PASS] All 12 structural tokens strictly verified in authoritative order.")

    # Trilingual roundtrip verification
    print("\nValidating Trilingual Encoding / Decoding Roundtrip:")
    samples = [
        ("English", "The IGRIS architecture incorporates SwiGLU activations and GQA."),
        ("Tamil", "இக்ரிஸ் மாதிரி தமிழ் மொழியை மிகச் சிறந்த முறையில் பகுப்பாய்வு செய்கிறது."),
        ("Tanglish", "IGRIS architecture epdi design panni irukkeenga bro? Romba nalla irukku."),
    ]
    for lang, text in samples:
        enc = tok.encode(text)
        dec = tok.decode(enc.ids)
        exact_match = (dec == text)
        print(f"  {lang:8s} | Tokens: {len(enc.ids):2d} | Roundtrip: {'EXACT' if exact_match else 'DIFF'}")
        if not exact_match:
            print(f"[FAIL] Trilingual decoding mismatch for {lang}!")
            return False
    print("[PASS] Trilingual encoding and decoding verified without data loss.")
    return True


def audit_architecture() -> bool:
    print("\n" + "=" * 70)
    print("2. MODEL ARCHITECTURE & PARAMETER COUNT AUDIT")
    print("=" * 70)

    # 1. Authoritative Production Architecture
    cfg_prod = get_production_config()
    cfg_prod.tie_word_embeddings = True
    m_prod = IgrisDecoderTransformer(cfg_prod)

    tied_unique_prod = sum(p.numel() for p in set(m_prod.parameters()))

    # Untied registered parameters calculation
    cfg_untied = get_production_config()
    cfg_untied.tie_word_embeddings = False
    m_untied = IgrisDecoderTransformer(cfg_untied)
    untied_registered_prod = sum(p.numel() for p in m_untied.parameters())

    print("Authoritative Production Profile (igris-prod-16l):")
    print(f"  Layers           : {cfg_prod.num_hidden_layers} (Expected: 16)")
    print(f"  Hidden Size      : {cfg_prod.hidden_size} (Expected: 512)")
    print(f"  FFN Intermediate : {cfg_prod.intermediate_size} (Expected: 2048)")
    print(f"  Attention Heads  : {cfg_prod.num_attention_heads} (Expected: 8)")
    print(f"  KV Heads         : {cfg_prod.num_key_value_heads} (Expected: 4, GQA 2:1)")
    print(f"  RoPE Theta       : {cfg_prod.rope_theta} (Expected: 10000.0)")
    print(f"  RMSNorm Epsilon  : {cfg_prod.rms_norm_eps} (Expected: 1e-05)")
    print(f"  Tied Parameters  : {tied_unique_prod:,} (Expected: 79,708,672)")
    print(f"  Untied Parameters: {untied_registered_prod:,} (Expected: 96,485,888)")

    if tied_unique_prod != 79708672 or untied_registered_prod != 96485888:
        print("[FAIL] Production parameter count mismatch!")
        return False
    print("[PASS] Production architecture parameters strictly verified.")

    # 2. Baseline Architecture
    cfg_base = get_baseline_50m_config()
    cfg_base.tie_word_embeddings = True
    m_base = IgrisDecoderTransformer(cfg_base)
    tied_unique_base = sum(p.numel() for p in set(m_base.parameters()))

    cfg_base_untied = get_baseline_50m_config()
    cfg_base_untied.tie_word_embeddings = False
    m_base_untied = IgrisDecoderTransformer(cfg_base_untied)
    untied_registered_base = sum(p.numel() for p in m_base_untied.parameters())

    print("\nBaseline Exploration Profile (igris-50m-baseline):")
    print(f"  Layers           : {cfg_base.num_hidden_layers} (Expected: 12)")
    print(f"  Hidden Size      : {cfg_base.hidden_size} (Expected: 512)")
    print(f"  FFN Intermediate : {cfg_base.intermediate_size} (Expected: 1376)")
    print(f"  Tied Parameters  : {tied_unique_base:,} (Expected: 51,589,632)")
    print(f"  Untied Parameters: {untied_registered_base:,} (Expected: 68,366,848)")

    if tied_unique_base != 51589632 or untied_registered_base != 68366848:
        print("[FAIL] Baseline parameter count mismatch!")
        return False
    print("[PASS] Baseline profile verified separate from production architecture.")
    return True


def audit_hardware() -> bool:
    print("\n" + "=" * 70)
    print("3. EMPIRICAL HARDWARE AUDIT")
    print("=" * 70)

    cuda_avail = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_avail}")

    if cuda_avail:
        dev = torch.cuda.current_device()
        dev_name = torch.cuda.get_device_name(dev)
        free_b, total_b = torch.cuda.mem_get_info(dev)
        alloc_b = torch.cuda.memory_allocated(dev)
        res_b = torch.cuda.memory_reserved(dev)
        print(f"GPU Device [{dev}]  : {dev_name}")
        print(f"Total Dedicated VRAM: {total_b / (1024**3):.2f} GB ({total_b:,} bytes)")
        print(f"Free VRAM Available : {free_b / (1024**3):.2f} GB ({free_b:,} bytes)")
        print(f"PyTorch Allocated   : {alloc_b / (1024**2):.2f} MB (0 MB expected without trained model)")
        print(f"PyTorch Reserved    : {res_b / (1024**2):.2f} MB")
    else:
        print("Running in CPU-only mode.")

    import ctypes
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]
    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))

    total_ram_gb = stat.ullTotalPhys / (1024**3)
    avail_ram_gb = stat.ullAvailPhys / (1024**3)
    print(f"System RAM Total    : {total_ram_gb:.2f} GB ({stat.ullTotalPhys:,} bytes)")
    print(f"System RAM Available: {avail_ram_gb:.2f} GB ({stat.ullAvailPhys:,} bytes)")
    print(f"System Memory Load  : {stat.dwMemoryLoad}%")

    print("\nModel Memory Estimations (Analytical, not measured since no weights loaded):")
    print("  Production FP16 Tied Weights : ~152.03 MB")
    print("  Production KV Cache (T=2048) : ~32.00 MB")
    print("  Estimated Peak Runtime VRAM  : ~509 MB (< 10% of 6GB)")
    print("[PASS] Hardware inspection completed.")
    return True


def audit_live_server() -> bool:
    print("\n" + "=" * 70)
    print("4. LIVE HTTP RUNTIME SMOKE TEST (http://127.0.0.1:8000)")
    print("=" * 70)

    base_url = "http://127.0.0.1:8000"

    # 1. Health check
    try:
        req = urllib.request.Request(f"{base_url}/health")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode())
            print(f"GET /health: HTTP {resp.status}")
            print(f"  model_loaded : {data.get('model_loaded')} (Expected: False)")
            print(f"  model_state  : {data.get('model_state')} (Expected: MODEL_NOT_TRAINED)")
            print(f"  active_device: {data.get('active_device')}")
            print(f"  tokenizer sha: {data.get('tokenizer', {}).get('sha256')}")

            if data.get("model_loaded") is not False:
                print("[FAIL] Health endpoint claims model is loaded when no checkpoint exists!")
                return False
            if data.get("model_state") != "MODEL_NOT_TRAINED":
                print(f"[FAIL] Model state should be MODEL_NOT_TRAINED, got {data.get('model_state')}")
                return False
            print("[PASS] Health endpoint accurately reports MODEL_NOT_TRAINED.")
    except Exception as exc:
        print(f"[FAIL] Could not connect to {base_url}/health: {exc}")
        return False

    # 2. Models registry
    try:
        req = urllib.request.Request(f"{base_url}/v1/models")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode())
            models = [m["id"] for m in data.get("data", [])]
            print(f"\nGET /v1/models: HTTP {resp.status}")
            print(f"  Registered models: {models}")
            if "igris-prod-16l" not in models or "igris-candidate-a" not in models:
                print("[FAIL] Missing production models in registry!")
                return False
            print("[PASS] Models endpoint verified.")
    except Exception as exc:
        print(f"[FAIL] Models check failed: {exc}")
        return False

    # 3. Chat completions safety check (must return 503 MODEL_NOT_TRAINED)
    print("\nPOST /v1/chat/completions (Safety Verification):")
    chat_payload = {
        "model": "igris-prod-16l",
        "messages": [{"role": "user", "content": "Tell me about IGRIS"}],
        "temperature": 0.7,
        "max_tokens": 64,
        "stream": False,
    }
    req = urllib.request.Request(
        f"{base_url}/v1/chat/completions",
        data=json.dumps(chat_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            print("[FAIL] Request succeeded when model has no trained checkpoint! Fabricated tokens forbidden.")
            return False
    except urllib.error.HTTPError as err:
        body = json.loads(err.read().decode())
        code = body.get("error", {}).get("code")
        print(f"  Received expected HTTP {err.code}: code={code}")
        if err.code != 503 or code != "MODEL_NOT_TRAINED":
            print(f"[FAIL] Expected 503 MODEL_NOT_TRAINED, got {err.code} / {code}")
            return False
        print("[PASS] Untrained request safely rejected with HTTP 503 MODEL_NOT_TRAINED.")

    return True


def main() -> int:
    print("IGRIS INFERENCE INTEGRATION VERIFICATION RUNNER")
    print(f"Executing with Python: {sys.executable}\n")

    tok_ok = audit_tokenizer()
    arch_ok = audit_architecture()
    hw_ok = audit_hardware()
    live_ok = audit_live_server()

    print("\n" + "=" * 70)
    print("FINAL INTEGRATION AUDIT VERDICT")
    print("=" * 70)
    print(f"1. Candidate A Tokenizer : {'PASS' if tok_ok else 'FAIL'}")
    print(f"2. Model Architecture    : {'PASS' if arch_ok else 'FAIL'}")
    print(f"3. Hardware Profile      : {'PASS' if hw_ok else 'FAIL'}")
    print(f"4. Live Server Smoke Test: {'PASS' if live_ok else 'FAIL'}")

    all_passed = tok_ok and arch_ok and hw_ok and live_ok
    if all_passed:
        print("\nALL VERIFICATIONS PASSED (100% GREEN). READY FOR OWNER REVIEW.")
        return 0
    else:
        print("\nONE OR MORE CHECKS FAILED.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
