from __future__ import annotations
import ast
import json
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_ROOT

SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules"}
TOKENS = (
    "candidate_a", "candidate_b", "sentencepiece", "tokenizer",
    "bytelevel", "rawbinary", "raw_binary", "adapter", "codec",
)

def safe_rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)

def main() -> int:
    if not ROOT.is_dir():
        print(json.dumps({"status": "FAIL_ROOT_NOT_FOUND", "root": str(ROOT)}, indent=2))
        return 2

    py_files = []
    for p in ROOT.rglob("*.py"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        py_files.append(p)

    records = []
    for p in sorted(py_files):
        rel = safe_rel(p)
        low = rel.lower()
        if not any(t in low for t in TOKENS) and "test" not in low and "script" not in low:
            continue
        rec = {"file": rel, "classes": [], "functions": [], "imports": [],
               "syntax": "OK", "parse_error": None}
        try:
            tree = ast.parse(p.read_text(encoding="utf-8-sig"), filename=str(p))
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    rec["classes"].append(node.name)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    rec["functions"].append(node.name)
                elif isinstance(node, ast.Import):
                    rec["imports"].extend(a.name for a in node.names)
                elif isinstance(node, ast.ImportFrom):
                    rec["imports"].append(node.module or "")
            rec["classes"] = sorted(set(rec["classes"]))
            rec["functions"] = sorted(set(rec["functions"]))
            rec["imports"] = sorted(set(x for x in rec["imports"] if x))
        except Exception as e:
            rec["syntax"] = "FAIL"
            rec["parse_error"] = f"{type(e).__name__}: {e}"
        records.append(rec)

    all_text = "\n".join(
        p.read_text(encoding="utf-8-sig", errors="replace")
        for p in py_files
    ).lower()

    deps = {
        "tokenizers": "tokenizers" in all_text,
        "sentencepiece": "sentencepiece" in all_text,
        "unicodedata2": "unicodedata2" in all_text,
        "regex": "regex" in all_text,
        "torch": "torch" in all_text,
    }
    result = {
        "status": "PREFLIGHT_COMPLETE",
        "root": str(ROOT),
        "python_files_found": len(py_files),
        "candidate_test_and_adapter_files": len(records),
        "dependency_references_in_source": deps,
        "files": records,
        "training_started": False,
        "files_modified": False,
        "training_authorized": False,
        "next_action": "Review this inventory, then run exact Candidate A/B integration tests against identified adapters."
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
