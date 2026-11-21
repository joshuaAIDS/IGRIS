import hashlib
import json
from tokenizers import Tokenizer

CAND_A = "artifacts/tokenizer/candidate_a/tokenizer.json"
CAND_B = "artifacts/tokenizer/candidate_b/tokenizer.model"
EXP_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
EXP_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

EXPECTED_STRUCTURAL = [
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

def hash_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def check_invariants():
    hash_a = hash_file(CAND_A)
    hash_b = hash_file(CAND_B)
    
    assert hash_a == EXP_A_HASH, f"Candidate A hash mismatch: {hash_a} != {EXP_A_HASH}"
    assert hash_b == EXP_B_HASH, f"Candidate B hash mismatch: {hash_b} != {EXP_B_HASH}"
    
    tok_a = Tokenizer.from_file(CAND_A)
    structural_verified = []
    for expected_id, expected_token in EXPECTED_STRUCTURAL:
        actual_id = tok_a.token_to_id(expected_token)
        actual_token = tok_a.id_to_token(expected_id)
        assert actual_id == expected_id, f"Structural token ID mismatch for {expected_token}: {actual_id} != {expected_id}"
        assert actual_token == expected_token, f"Structural token string mismatch for {expected_id}: {actual_token} != {expected_token}"
        structural_verified.append({"id": expected_id, "token": expected_token, "status": "VERIFIED"})
        
    print(json.dumps({
        "candidate_a_sha256": hash_a,
        "candidate_a_match": hash_a == EXP_A_HASH,
        "candidate_b_sha256": hash_b,
        "candidate_b_match": hash_b == EXP_B_HASH,
        "structural_tokens_0_to_11": structural_verified,
        "vocab_size": tok_a.get_vocab_size()
    }, indent=2))

if __name__ == "__main__":
    check_invariants()
