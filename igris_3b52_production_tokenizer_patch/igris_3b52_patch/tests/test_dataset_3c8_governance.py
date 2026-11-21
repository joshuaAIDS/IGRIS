import csv
import hashlib
from pathlib import Path
import pytest

PATCH_ROOT = Path(__file__).resolve().parent.parent

CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

FOUR_CORE_ROLES = [
    "DATA_CUSTODIAN",
    "LEGAL_GOVERNANCE",
    "SECURITY_PRIVACY",
    "CHIEF_ARCHITECT",
]

NINE_LICENSE_CATEGORIES = {
    "CC0",
    "CC-BY",
    "Apache-2.0",
    "MIT",
    "Public Domain",
    "ShareAlike",
    "GPL",
    "ODC-By",
    "Other / Unknown",
}

SIX_PERMISSION_FIELDS = [
    "tokenizer_vocab_training",
    "tokenizer_fertility_evaluation",
    "tokenizer_regression_evaluation",
    "supervised_fine_tuning",
    "alignment_evaluation",
    "safety_evaluation",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_3c8_deliverables_exist():
    required_files = [
        "IGRIS_3C8_LEGAL_CORRECTION_REPORT.md",
        "INDIA_COPYRIGHT_REVIEW.md",
        "DATASET_LICENSE_CLASSIFICATION_V3.csv",
        "PIPELINE_AUTHORIZATION_MATRIX_V2.csv",
        "GUTENBERG_JURISDICTION_REVIEW_V2.md",
        "IGRIS_3C8_STATUS.md",
    ]
    for rel_path in required_files:
        p = PATCH_ROOT / rel_path
        assert p.is_file(), f"Missing required 3C.8 file: {rel_path}"
        assert p.stat().st_size > 0, f"Empty 3C.8 file: {rel_path}"


def test_india_copyright_review_content():
    content = (PATCH_ROOT / "INDIA_COPYRIGHT_REVIEW.md").read_text(encoding="utf-8")
    assert "Section 22" in content
    assert "Life + 60" in content or "Life+60" in content or "sixty years" in content
    assert "1965" in content
    assert "Section 23" in content
    assert "Section 24" in content
    assert "Section 28" in content
    assert "Section 57" in content
    assert "joint authorship" in content.lower()
    assert "posthumous" in content.lower()
    assert "anonymous" in content.lower()


def test_dataset_license_classification_v3_schema_and_counts():
    csv_path = PATCH_ROOT / "DATASET_LICENSE_CLASSIFICATION_V3.csv"
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 32, f"Expected 32 sources in license classification, got {len(rows)}"

    expected_cols = [
        "source_id",
        "dataset_name",
        "canonical_category",
        "license_category",
        "exact_license_and_version",
        "attribution_obligations",
        "sharealike_obligations",
        "copyleft_obligations",
        "commercial_use_evidence",
        "underlying_content_rights",
        "redistribution_conditions",
        "primary_status",
    ]
    for col in expected_cols:
        assert col in reader.fieldnames, f"Missing column in V3 license classification: {col}"

    observed_categories = {r["license_category"] for r in rows}
    assert observed_categories == NINE_LICENSE_CATEGORIES, (
        f"Missing or unexpected license categories. Expected {NINE_LICENSE_CATEGORIES}, got {observed_categories}"
    )

    for r in rows:
        if r["license_category"] in ["CC-BY", "Apache-2.0"]:
            combined = (r["attribution_obligations"] + " " + r["commercial_use_evidence"]).lower()
            assert "not unrestricted" in combined, (
                f"Row {r['source_id']} must explicitly state that {r['license_category']} is NOT unrestricted"
            )


def test_pipeline_authorization_matrix_v2_schema_and_boundaries():
    csv_path = PATCH_ROOT / "PIPELINE_AUTHORIZATION_MATRIX_V2.csv"
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 32, f"Expected 32 sources in pipeline authorization matrix, got {len(rows)}"

    for col in SIX_PERMISSION_FIELDS:
        assert col in reader.fieldnames, f"Missing permission field: {col}"

    row_map = {r["source_id"]: r for r in rows}

    # SFT, Alignment, and Safety must remain NOT AUTHORIZED across all 32 sources
    for r in rows:
        assert "NOT AUTHORIZED" in r["supervised_fine_tuning"], (
            f"SFT must be NOT AUTHORIZED for {r['source_id']}"
        )
        assert "NOT AUTHORIZED" in r["alignment_evaluation"], (
            f"Alignment must be NOT AUTHORIZED for {r['source_id']}"
        )
        assert "NOT AUTHORIZED" in r["safety_evaluation"], (
            f"Safety must be NOT AUTHORIZED for {r['source_id']}"
        )

    # SRC-CV-04 isolation checks
    cv04 = row_map["SRC-CV-04"]
    assert cv04["tokenizer_vocab_training"] == "STRICTLY_PROHIBITED"
    assert cv04["tokenizer_fertility_evaluation"] == "ELIGIBLE_ISOLATED_PROMPTS_ONLY"
    assert "NOT AUTHORIZED" in cv04["supervised_fine_tuning"]
    assert "PRIMARY BENCHMARK" in cv04["alignment_evaluation"]
    assert "SAFETY BENCHMARK" in cv04["safety_evaluation"]
    assert "SRC-CV-04-CHOSEN-PROMPTS-ISOLATED" in cv04["authorization_boundary_notes"]

    # SRC-CD-02 contamination guard checks
    cd02 = row_map["SRC-CD-02"]
    assert cd02["tokenizer_vocab_training"] == "STRICTLY_PROHIBITED"
    assert cd02["tokenizer_fertility_evaluation"] == "ELIGIBLE_PENDING_APPROVAL"
    assert "NOT AUTHORIZED" in cd02["supervised_fine_tuning"]


def test_gutenberg_jurisdiction_review_v2_content():
    content = (PATCH_ROOT / "GUTENBERG_JURISDICTION_REVIEW_V2.md").read_text(encoding="utf-8")
    assert "1928" in content, "Pre-1928 US rule must be specified"
    assert "1965" in content, "1965 Indian Section 22 cut-off must be specified"
    assert "1955" in content, "1955 UK/EU Life+70 cut-off must be specified"
    assert "zero copyright risk globally" in content.lower(), "Must address and reject zero copyright risk globally"
    assert "trademark" in content.lower()
    assert "translator" in content.lower()
    assert "posthumous" in content.lower() or "section 24" in content.lower()


def test_four_approval_roles_preserved():
    matrix_text = (PATCH_ROOT / "PIPELINE_AUTHORIZATION_MATRIX_V2.csv").read_text(encoding="utf-8")
    status_text = (PATCH_ROOT / "IGRIS_3C8_STATUS.md").read_text(encoding="utf-8")
    report_text = (PATCH_ROOT / "IGRIS_3C8_LEGAL_CORRECTION_REPORT.md").read_text(encoding="utf-8")
    for role in FOUR_CORE_ROLES:
        assert role in status_text, f"Role {role} missing in IGRIS_3C8_STATUS.md"
        assert role in report_text, f"Role {role} missing in IGRIS_3C8_LEGAL_CORRECTION_REPORT.md"


def test_candidate_invariants_preserved():
    cand_a = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    cand_b = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
    assert cand_a.exists(), f"Candidate A missing at {cand_a}"
    assert cand_b.exists(), f"Candidate B missing at {cand_b}"
    assert sha256_file(cand_a) == CANDIDATE_A_HASH
    assert sha256_file(cand_b) == CANDIDATE_B_HASH
