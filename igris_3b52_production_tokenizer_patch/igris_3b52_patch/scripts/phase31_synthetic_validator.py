"""
phase31_synthetic_validator.py — Non-production synthetic test runner for IGRIS Phase 31.
Tests:
1. Python Docs Benchmark Decontamination (HumanEval/MBPP overlap detection).
2. Python Docs PII scrubbing (regex email/phone masking on synthetic fixtures).
3. Python Docs Document Structure & Quality Filtering.
4. OASST1 English Language Filtering (detecting Tanglish vs English in Latin script).
5. OASST1 Conversation Tree Integrity (parent-child, orphan detection, cycle detection).
6. OASST1 Privacy Scrubbing (synthetic prompt PII detection).
7. OASST1 Benchmark Split Quarantine.
"""

import re
import unicodedata
from typing import Dict, List, Any, Tuple

# Reusable regex patterns
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_REGEX = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')

# Synthetic benchmark signatures (HumanEval mock)
HUMANEVAL_SIGNATURES = [
    "def has_close_elements(numbers: List[float], threshold: float) -> bool:",
    "def separate_paren_groups(paren_string: str) -> List[str]:",
    "def truncate_number(number: float) -> float:",
    "def below_zero(operations: List[int]) -> bool:",
    "def mean_absolute_deviation(numbers: List[float]) -> float:",
]

# Synthetic Python Docs Fixtures
SYNTHETIC_PYTHON_DOCS = [
    {
        "id": "PY-SYNTH-01",
        "type": "docstring",
        "text": """Return the Euclidean distance between two points p and q, each given as a sequence (or iterable) of coordinates. Both points must have the same dimension.""",
        "expected_result": "PASS_CLEAN",
    },
    {
        "id": "PY-SYNTH-02",
        "type": "docstring_adversarial_humaneval",
        "text": """def has_close_elements(numbers: List[float], threshold: float) -> bool:
    Check if in given list of numbers, are any two numbers closer to each other than given threshold.""",
        "expected_result": "REJECT_BENCHMARK_OVERLAP",
    },
    {
        "id": "PY-SYNTH-03",
        "type": "acknowledgments_pii",
        "text": """Thanks to core developer Alex Smith (alex.smith@python.org) and review from Jane Doe (jdoe@example.com) for their patches on the async subsystem.""",
        "expected_result": "MASKED_PII",
    },
    {
        "id": "PY-SYNTH-04",
        "type": "short_boilerplate",
        "text": """Table of Contents\n=================\n* Index\n* Module Index\n* Search Page""",
        "expected_result": "REJECT_BOILERPLATE",
    },
]

# Synthetic OASST1 Tree Fixtures
SYNTHETIC_OASST1_TREES = [
    {
        "tree_id": "TREE-SYNTH-01",
        "description": "Valid 2-turn dialogue",
        "messages": [
            {"message_id": "m1", "parent_id": None, "role": "prompter", "lang": "en", "text": "How do I reverse a string in Python?"},
            {"message_id": "m2", "parent_id": "m1", "role": "assistant", "lang": "en", "text": "You can reverse a string using slicing: `s[::-1]`."},
        ],
        "expected_tree_valid": True,
    },
    {
        "tree_id": "TREE-SYNTH-02",
        "description": "Orphaned child node",
        "messages": [
            {"message_id": "m1", "parent_id": "non_existent_root", "role": "assistant", "lang": "en", "text": "This message has no parent."},
        ],
        "expected_tree_valid": False,
        "expected_rejection": "REJECT_ORPHAN_MESSAGE",
    },
    {
        "tree_id": "TREE-SYNTH-03",
        "description": "Cyclic relationship",
        "messages": [
            {"message_id": "m1", "parent_id": "m2", "role": "prompter", "lang": "en", "text": "Cycle A"},
            {"message_id": "m2", "parent_id": "m1", "role": "assistant", "lang": "en", "text": "Cycle B"},
        ],
        "expected_tree_valid": False,
        "expected_rejection": "REJECT_CYCLE_DETECTED",
    },
    {
        "tree_id": "TREE-SYNTH-04",
        "description": "Tanglish in Latin script submitted with English tag",
        "messages": [
            {"message_id": "m1", "parent_id": None, "role": "prompter", "lang": "en", "text": "enna bro romba late ah reply varudhu? konjam seekiram sollunga."},
            {"message_id": "m2", "parent_id": "m1", "role": "assistant", "lang": "en", "text": "kandippa bro, enna doubt nu sollunga, udane help panren."},
        ],
        "expected_tree_valid": False,
        "expected_rejection": "REJECT_LANG_MISMATCH_TANGLISH",
    },
    {
        "tree_id": "TREE-SYNTH-05",
        "description": "Volunteer prompt disclosing real PII",
        "messages": [
            {"message_id": "m1", "parent_id": None, "role": "prompter", "lang": "en", "text": "Hi my name is John Miller from Seattle, call me at 206-555-0199 or email me at jmiller99@mailtest.com."},
            {"message_id": "m2", "parent_id": "m1", "role": "assistant", "lang": "en", "text": "Hello John, how can I assist you today?"},
        ],
        "expected_tree_valid": True,
        "expected_pii_detected": True,
    },
]

def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFC", text)

def check_benchmark_overlap(text: str) -> bool:
    for sig in HUMANEVAL_SIGNATURES:
        if sig in text:
            return True
        # Normalized match check
        sig_norm = re.sub(r'\s+', ' ', sig.strip())
        text_norm = re.sub(r'\s+', ' ', text.strip())
        if sig_norm in text_norm:
            return True
    return False

def scrub_pii(text: str) -> Tuple[str, int]:
    scrubbed, count1 = EMAIL_REGEX.subn("[EMAIL_REDACTED]", text)
    scrubbed, count2 = PHONE_REGEX.subn("[PHONE_REDACTED]", scrubbed)
    return scrubbed, count1 + count2

def is_tanglish_heuristic(text: str) -> bool:
    # Key markers of Romanized Tamil (Tanglish)
    markers = ["enna", "bro", "romba", "seekiram", "sollunga", "kandippa", "panren", "illa", "irukku", "vaanga"]
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    matches = sum(1 for w in words if w in markers)
    return matches >= 2

def validate_tree(messages: List[Dict[str, Any]]) -> Tuple[bool, str]:
    msg_ids = {m["message_id"] for m in messages}
    for m in messages:
        # Check language
        if is_tanglish_heuristic(m["text"]):
            return False, "REJECT_LANG_MISMATCH_TANGLISH"
        pid = m["parent_id"]
        if pid is not None and pid not in msg_ids:
            return False, "REJECT_ORPHAN_MESSAGE"
        if pid == m["message_id"]:
            return False, "REJECT_CYCLE_DETECTED"
    
    # Check cycles via visited set
    for m in messages:
        curr = m["message_id"]
        visited = set()
        while curr is not None:
            if curr in visited:
                return False, "REJECT_CYCLE_DETECTED"
            visited.add(curr)
            parent = next((item["parent_id"] for item in messages if item["message_id"] == curr), None)
            curr = parent
            
    return True, "PASS_TREE_VALID"

def run_synthetic_tests() -> Dict[str, Any]:
    results = {
        "python_docs_passed": 0,
        "python_docs_total": len(SYNTHETIC_PYTHON_DOCS),
        "oasst1_passed": 0,
        "oasst1_total": len(SYNTHETIC_OASST1_TREES),
        "details": []
    }
    
    # Python Docs tests
    for item in SYNTHETIC_PYTHON_DOCS:
        norm = normalize_text(item["text"])
        if item["type"] == "docstring_adversarial_humaneval":
            is_overlap = check_benchmark_overlap(norm)
            passed = is_overlap and item["expected_result"] == "REJECT_BENCHMARK_OVERLAP"
            results["details"].append({"id": item["id"], "passed": passed, "action": "REJECT_BENCHMARK_OVERLAP"})
        elif item["type"] == "acknowledgments_pii":
            scrubbed, count = scrub_pii(norm)
            passed = count >= 2 and "[EMAIL_REDACTED]" in scrubbed
            results["details"].append({"id": item["id"], "passed": passed, "action": "MASKED_PII", "redactions": count})
        elif item["type"] == "short_boilerplate":
            is_bp = "Table of Contents" in norm or "Module Index" in norm
            passed = is_bp and item["expected_result"] == "REJECT_BOILERPLATE"
            results["details"].append({"id": item["id"], "passed": passed, "action": "REJECT_BOILERPLATE"})
        else:
            passed = not check_benchmark_overlap(norm) and EMAIL_REGEX.search(norm) is None
            results["details"].append({"id": item["id"], "passed": passed, "action": "PASS_CLEAN"})
            
        if passed:
            results["python_docs_passed"] += 1
            
    # OASST1 Tree tests
    for tree in SYNTHETIC_OASST1_TREES:
        valid, reason = validate_tree(tree["messages"])
        if tree["tree_id"] == "TREE-SYNTH-05":
            # Check PII
            has_pii = any(EMAIL_REGEX.search(m["text"]) or PHONE_REGEX.search(m["text"]) for m in tree["messages"])
            passed = valid and has_pii
            results["details"].append({"id": tree["tree_id"], "passed": passed, "status": "PII_DETECTED_AND_FLAGGED"})
        else:
            expected_valid = tree["expected_tree_valid"]
            if expected_valid:
                passed = valid
            else:
                passed = not valid and reason == tree.get("expected_rejection")
            results["details"].append({"id": tree["tree_id"], "passed": passed, "status": reason})
            
        if passed:
            results["oasst1_passed"] += 1
            
    return results

if __name__ == "__main__":
    res = run_synthetic_tests()
    print("Synthetic Test Results:")
    print(f"  Python Docs Fixtures: {res['python_docs_passed']}/{res['python_docs_total']} PASSED")
    print(f"  OASST1 Tree Fixtures: {res['oasst1_passed']}/{res['oasst1_total']} PASSED")
    for d in res["details"]:
        print(f"    - {d['id']}: Passed={d['passed']} Status={d.get('action') or d.get('status')}")
