"""Frozen acceptance constants for IGRIS v2.2.28 tokenizer candidates."""

PROJECT_VERSION = "2.2.28"
ACCEPTANCE_SPEC_VERSION = "1.0.4"
INTEGRATION_CONTRACT_VERSION = "1.0"

VOCAB_SIZE = 32_768
UNICODE_VERSION = "15.1.0"

STRUCTURAL_TOKENS = (
    "<|pad|>",
    "<|begin_of_text|>",
    "<|end_of_text|>",
    "<think>",
    "</think>",
    "<action>",
    "</action>",
    "<action_result>",
    "</action_result>",
    "<|system|>",
    "<|user|>",
    "<|assistant|>",
)
STRUCTURAL_TOKEN_IDS = {token: i for i, token in enumerate(STRUCTURAL_TOKENS)}
STRUCTURAL_ID_SET = frozenset(range(12))
CONTENT_ID_MIN = 12
CONTENT_ID_MAX_EXCLUSIVE = VOCAB_SIZE

CANDIDATES = ("A", "B")
STATUSES = ("PASS", "FAIL", "NOT TESTED", "BLOCKED")

TEST_GROUPS = (
    "TS-VAL", "TS-UNI", "TS-SEC", "TS-BAT", "TS-REN",
    "TS-BIN", "TS-META", "TS-API", "TS-DET", "TS-ERR",
)
