"""Tests for IGRIS Dataset Inventory Management and Schema Validation.

Milestone: 3B.60 — Dataset Authorization & Inventory Preparation
Module: tests/test_dataset_inventory.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path
import pytest

# Add patch src and scripts
_PATCH_ROOT = Path(__file__).resolve().parents[1]
_PATCH_SRC = str(_PATCH_ROOT / "src")
_PATCH_SCRIPTS = str(_PATCH_ROOT / "scripts")
for p in [_PATCH_SRC, _PATCH_SCRIPTS]:
    if p not in sys.path:
        sys.path.insert(0, p)

from dataset_inventory import (
    APPROVED_CATEGORIES,
    VALID_AUTHORIZATION_STATUSES,
    VALID_SCREENING_STATUSES,
    DatasetInventory,
    DatasetInventoryRecord,
    generate_manifest,
)

INVENTORY_TEMPLATE_PATH = _PATCH_ROOT / "DATASET_INVENTORY_TEMPLATE.csv"


class TestDatasetInventory:
    """Test suite for dataset inventory records and templates."""

    def test_inventory_template_exists_and_loads(self):
        assert INVENTORY_TEMPLATE_PATH.is_file(), f"Template missing at {INVENTORY_TEMPLATE_PATH}"
        inv = DatasetInventory.load_from_csv(INVENTORY_TEMPLATE_PATH)
        assert len(inv.records) >= 6
        errors = inv.validate_inventory()
        assert errors == [], f"Validation errors found in template: {errors}"

    def test_all_10_approved_categories(self):
        inv = DatasetInventory()
        for idx, cat in enumerate(APPROVED_CATEGORIES):
            rec = DatasetInventoryRecord(
                dataset_id=f"DS-TEST-{idx:03d}",
                dataset_name=f"test_dataset_{idx}",
                version="1.0.0",
                category=cat,
                language="ta" if "Tamil" in cat else "en",
                script="Taml" if "Tamil" in cat else "Latn",
                file_path=f"synthetic/{cat.lower().replace(' ', '_')}.jsonl",
                format="jsonl",
                encoding="UTF-8",
                line_count=100,
                character_count=5000,
                byte_size=12000,
                sha256_checksum="a" * 64,
                license="MIT",
                owner="Engineering",
                custodian="custodian@igris.internal",
                authorization_status="APPROVED",
                approval_ticket_id="GOV-TEST-01",
                screening_status="SCREENED_CLEAN",
            )
            inv.add_record(rec)
        assert len(inv.records) == 10
        assert inv.validate_inventory() == []

    def test_unapproved_category_rejected(self):
        rec = DatasetInventoryRecord(
            dataset_id="DS-INVALID-01",
            dataset_name="invalid_cat",
            version="1.0.0",
            category="Unapproved Category",
            language="en",
            script="Latn",
            file_path="synthetic/test.jsonl",
            format="jsonl",
            encoding="UTF-8",
            line_count=10,
            character_count=100,
            byte_size=200,
            sha256_checksum="b" * 64,
            license="MIT",
            owner="Engineering",
            custodian="custodian@igris.internal",
            authorization_status="APPROVED",
            approval_ticket_id="GOV-TEST-01",
            screening_status="SCREENED_CLEAN",
        )
        with pytest.raises(ValueError, match="not one of the approved categories"):
            DatasetInventory().add_record(rec)

    def test_invalid_sha256_checksum_rejected(self):
        # 63 characters instead of 64
        rec = DatasetInventoryRecord(
            dataset_id="DS-INVALID-02",
            dataset_name="bad_checksum",
            version="1.0.0",
            category="English",
            language="en",
            script="Latn",
            file_path="synthetic/test.jsonl",
            format="jsonl",
            encoding="UTF-8",
            line_count=10,
            character_count=100,
            byte_size=200,
            sha256_checksum="c" * 63,
            license="MIT",
            owner="Engineering",
            custodian="custodian@igris.internal",
            authorization_status="APPROVED",
            approval_ticket_id="GOV-TEST-01",
            screening_status="SCREENED_CLEAN",
        )
        with pytest.raises(ValueError, match="not a valid 64-character hexadecimal SHA-256 hash"):
            DatasetInventory().add_record(rec)

    def test_invalid_status_rejected(self):
        rec = DatasetInventoryRecord(
            dataset_id="DS-INVALID-03",
            dataset_name="bad_status",
            version="1.0.0",
            category="English",
            language="en",
            script="Latn",
            file_path="synthetic/test.jsonl",
            format="jsonl",
            encoding="UTF-8",
            line_count=10,
            character_count=100,
            byte_size=200,
            sha256_checksum="d" * 64,
            license="MIT",
            owner="Engineering",
            custodian="custodian@igris.internal",
            authorization_status="UNAUTHORIZED_STATUS",
            approval_ticket_id="GOV-TEST-01",
            screening_status="SCREENED_CLEAN",
        )
        with pytest.raises(ValueError, match="authorization_status 'UNAUTHORIZED_STATUS' is invalid"):
            DatasetInventory().add_record(rec)

    def test_invalid_screening_status_rejected(self):
        rec = DatasetInventoryRecord(
            dataset_id="DS-INVALID-04",
            dataset_name="bad_screening",
            version="1.0.0",
            category="English",
            language="en",
            script="Latn",
            file_path="synthetic/test.jsonl",
            format="jsonl",
            encoding="UTF-8",
            line_count=10,
            character_count=100,
            byte_size=200,
            sha256_checksum="e" * 64,
            license="MIT",
            owner="Engineering",
            custodian="custodian@igris.internal",
            authorization_status="APPROVED",
            approval_ticket_id="GOV-TEST-01",
            screening_status="NOT_SCREENED",
        )
        with pytest.raises(ValueError, match="screening_status 'NOT_SCREENED' is invalid"):
            DatasetInventory().add_record(rec)

    def test_non_utf8_encoding_rejected(self):
        rec = DatasetInventoryRecord(
            dataset_id="DS-INVALID-05",
            dataset_name="bad_encoding",
            version="1.0.0",
            category="English",
            language="en",
            script="Latn",
            file_path="synthetic/test.jsonl",
            format="jsonl",
            encoding="ISO-8859-1",
            line_count=10,
            character_count=100,
            byte_size=200,
            sha256_checksum="f" * 64,
            license="MIT",
            owner="Engineering",
            custodian="custodian@igris.internal",
            authorization_status="APPROVED",
            approval_ticket_id="GOV-TEST-01",
            screening_status="SCREENED_CLEAN",
        )
        with pytest.raises(ValueError, match="encoding must be 'UTF-8'"):
            DatasetInventory().add_record(rec)

    def test_negative_metrics_rejected(self):
        rec = DatasetInventoryRecord(
            dataset_id="DS-INVALID-06",
            dataset_name="negative_metric",
            version="1.0.0",
            category="English",
            language="en",
            script="Latn",
            file_path="synthetic/test.jsonl",
            format="jsonl",
            encoding="UTF-8",
            line_count=-5,
            character_count=100,
            byte_size=200,
            sha256_checksum="0" * 64,
            license="MIT",
            owner="Engineering",
            custodian="custodian@igris.internal",
            authorization_status="APPROVED",
            approval_ticket_id="GOV-TEST-01",
            screening_status="SCREENED_CLEAN",
        )
        with pytest.raises(ValueError, match="line_count must be >= 0"):
            DatasetInventory().add_record(rec)

    def test_filter_by_status_and_category(self):
        inv = DatasetInventory.load_from_csv(INVENTORY_TEMPLATE_PATH)
        approved = inv.filter_by_status("APPROVED")
        assert len(approved) >= 4
        tamil = inv.filter_by_category("Tamil")
        assert len(tamil) >= 1
        assert tamil[0].dataset_id == "DS-SYNTH-TM-001"

    def test_csv_save_and_reload(self):
        inv = DatasetInventory.load_from_csv(INVENTORY_TEMPLATE_PATH)
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as tf:
            tf_path = Path(tf.name)

        try:
            inv.save_to_csv(tf_path)
            reloaded = DatasetInventory.load_from_csv(tf_path)
            assert len(reloaded.records) == len(inv.records)
            for d_id, rec in inv.records.items():
                r_rec = reloaded.get_record(d_id)
                assert r_rec is not None
                assert r_rec.sha256_checksum == rec.sha256_checksum
                assert r_rec.byte_size == rec.byte_size
        finally:
            if tf_path.exists():
                tf_path.unlink()

    def test_manifest_generator_synthetic(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            f1 = td_path / "part_1.jsonl"
            f1.write_text("{\"text\": \"தமிழ் வாழ்க\"}\n", encoding="utf-8")
            f2 = td_path / "sub" / "part_2.txt"
            f2.parent.mkdir(parents=True, exist_ok=True)
            f2.write_text("Hello world\nSecond line\n", encoding="utf-8")

            mf_out = td_path / "manifest.json"
            manifest = generate_manifest(td_path, dataset_id="DS-TEST-GEN-01", output_manifest_path=mf_out)

            assert manifest["dataset_id"] == "DS-TEST-GEN-01"
            assert manifest["total_files"] == 2
            assert manifest["total_lines"] == 3
            assert len(manifest["manifest_sha256"]) == 64
            assert mf_out.is_file()

            # Verify deterministic computation
            f1_bytes = f1.read_bytes()
            expected_f1_hash = hashlib.sha256(f1_bytes).hexdigest()
            p1_entry = next(f for f in manifest["files"] if f["relative_path"] == "part_1.jsonl")
            assert p1_entry["sha256"] == expected_f1_hash
            assert p1_entry["byte_size"] == len(f1_bytes)
