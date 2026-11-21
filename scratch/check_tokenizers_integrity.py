import hashlib
import json
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
cand_a = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
cand_b = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
cand_exp = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"

def get_hash(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

print("Original Candidate A:   ", get_hash(cand_a))
print("Candidate B reference:  ", get_hash(cand_b))
print("Experimental Candidate A:", get_hash(cand_exp))

EXPECTED_CAND_A = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
EXPECTED_CAND_B = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"
EXPECTED_EXP = "3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce"

assert get_hash(cand_a) == EXPECTED_CAND_A
assert get_hash(cand_b) == EXPECTED_CAND_B
assert get_hash(cand_exp) == EXPECTED_EXP
print("[PASS] All 3 cryptographic hashes match expected exactly.")

# Inspect structural tokens
STRUCTURAL = [
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
    (11, "<|assistant|>")
]

# Check in Candidate A
with open(cand_a, encoding="utf-8") as f:
    data_a = json.load(f)
vocab_a = data_a["model"]["vocab"]
inv_vocab_a = {v: k for k, v in vocab_a.items()}

print("\nCandidate A Structural Tokens:")
for expected_id, expected_tok in STRUCTURAL:
    actual_tok = inv_vocab_a.get(expected_id)
    print(f"  ID {expected_id:2d}: expected {expected_tok:20s} actual {actual_tok}")
    assert actual_tok == expected_tok, f"Candidate A ID {expected_id} mismatch: {actual_tok} != {expected_tok}"

# Check in Experimental Candidate A
with open(cand_exp, encoding="utf-8") as f:
    data_exp = json.load(f)
vocab_exp = data_exp["model"]["vocab"]
inv_vocab_exp = {v: k for k, v in vocab_exp.items()}

print("\nExperimental Candidate A Structural Tokens:")
for expected_id, expected_tok in STRUCTURAL:
    actual_tok = inv_vocab_exp.get(expected_id)
    print(f"  ID {expected_id:2d}: expected {expected_tok:20s} actual {actual_tok}")
    assert actual_tok == expected_tok, f"Experimental Candidate A ID {expected_id} mismatch: {actual_tok} != {expected_tok}"

print("[PASS] Structural tokens IDs 0-11 verified in both tokenizers.")
