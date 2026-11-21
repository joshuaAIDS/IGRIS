#!/usr/bin/env python3
"""IGRIS Tokenizer Dataset Inventory Manager.

Milestone: 3B.60 — Dataset Authorization & Inventory Preparation
Module: scripts/dataset_inventory.py

Manages dataset inventory records, enforces schema validation, verifies
approved categories and checksum formats, and generates cryptographic manifests.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

# Approved 10 multilingual evaluation categories from Milestone 3B.59
APPROVED_CATEGORIES: Sequence[str] = (
    "Tamil",
    "English",
    "Tanglish",
    "Hindi",
    "Other Indian languages",
    "Multilingual mixed text",
    "Programming code",
    "Technical documentation",
    "Conversational text",
    "Emoji and Unicode edge cases",
)

VALID_AUTHORIZATION_STATUSES: Sequence[str] = (
    "LOCKED",
    "PENDING",
    "PENDING_REVIEW",
    "APPROVED",
    "REJECTED",
    "REVOKED",
)

VALID_SCREENING_STATUSES: Sequence[str] = (
    "SCREENED_CLEAN",
    "PENDING",
    "QUARANTINED",
    "FLAGGED",
)

HEX_64_REGEX = re.compile(r"^[0-9a-fA-F]{64}$")
SEMVER_REGEX = re.compile(r"^v?[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$")


@dataclass
class DatasetInventoryRecord:
    dataset_id: str
    dataset_name: str
    version: str
    category: str
    language: str
    script: str
    file_path: str
    format: str
    encoding: str
    line_count: int
    character_count: int
    byte_size: int
    sha256_checksum: str
    license: str
    owner: str
    custodian: str
    authorization_status: str
    approval_ticket_id: str
    screening_status: str

    def validate(self) -> List[str]:
        """Validate all fields of this inventory record according to 3B.60 specs."""
        errors: List[str] = []

        if not self.dataset_id or not self.dataset_id.strip():
            errors.append("dataset_id cannot be empty")
        elif not re.match(r"^[A-Za-z0-9_-]+$", self.dataset_id):
            errors.append(f"dataset_id '{self.dataset_id}' contains invalid characters")

        if not self.dataset_name or not self.dataset_name.strip():
            errors.append("dataset_name cannot be empty")

        if not SEMVER_REGEX.match(self.version):
            errors.append(f"version '{self.version}' is not valid semantic versioning (e.g. 1.0.0)")

        if self.category not in APPROVED_CATEGORIES:
            errors.append(
                f"category '{self.category}' is not one of the approved categories: {APPROVED_CATEGORIES}"
            )

        if self.encoding.upper() != "UTF-8":
            errors.append(f"encoding must be 'UTF-8', got '{self.encoding}'")

        if self.byte_size < 0:
            errors.append(f"byte_size must be >= 0, got {self.byte_size}")
        if self.line_count < 0:
            errors.append(f"line_count must be >= 0, got {self.line_count}")
        if self.character_count < 0:
            errors.append(f"character_count must be >= 0, got {self.character_count}")

        if not HEX_64_REGEX.match(self.sha256_checksum):
            errors.append(
                f"sha256_checksum '{self.sha256_checksum}' is not a valid 64-character hexadecimal SHA-256 hash"
            )

        if self.authorization_status not in VALID_AUTHORIZATION_STATUSES:
            errors.append(
                f"authorization_status '{self.authorization_status}' is invalid. Allowed: {VALID_AUTHORIZATION_STATUSES}"
            )

        if self.screening_status not in VALID_SCREENING_STATUSES:
            errors.append(
                f"screening_status '{self.screening_status}' is invalid. Allowed: {VALID_SCREENING_STATUSES}"
            )

        if not self.license or not self.license.strip():
            errors.append("license cannot be empty")

        if not self.custodian or not self.custodian.strip():
            errors.append("custodian cannot be empty")

        return errors


class DatasetInventory:
    """In-memory and file-based repository of dataset inventory records."""

    def __init__(self) -> None:
        self.records: Dict[str, DatasetInventoryRecord] = {}

    def add_record(self, record: DatasetInventoryRecord) -> None:
        errors = record.validate()
        if errors:
            raise ValueError(f"Invalid DatasetInventoryRecord: {'; '.join(errors)}")
        self.records[record.dataset_id] = record

    def get_record(self, dataset_id: str) -> Optional[DatasetInventoryRecord]:
        return self.records.get(dataset_id)

    def get_authorized_record(self, dataset_id: str) -> DatasetInventoryRecord:
        """Retrieve a dataset inventory record, strictly enforcing that it is APPROVED.

        Raises:
            KeyError: If dataset_id does not exist in inventory.
            PermissionError: If dataset is not in APPROVED state.
        """
        record = self.get_record(dataset_id)
        if record is None:
            raise KeyError(f"Dataset ID '{dataset_id}' not found in inventory")
        if record.authorization_status != "APPROVED":
            raise PermissionError(
                f"Access denied: Dataset '{dataset_id}' is in '{record.authorization_status}' state (expected 'APPROVED')"
            )
        return record

    def filter_by_status(self, status: str) -> List[DatasetInventoryRecord]:
        return [r for r in self.records.values() if r.authorization_status == status]

    def filter_by_category(self, category: str) -> List[DatasetInventoryRecord]:
        return [r for r in self.records.values() if r.category == category]

    def validate_inventory(self) -> List[str]:
        all_errors: List[str] = []
        for record_id, record in self.records.items():
            errs = record.validate()
            for err in errs:
                all_errors.append(f"[{record_id}] {err}")
        return all_errors

    @classmethod
    def load_from_csv(cls, csv_path: Union[str, Path]) -> "DatasetInventory":
        path = Path(csv_path)
        if not path.is_file():
            raise FileNotFoundError(f"Inventory CSV file not found: {path}")

        inventory = cls()
        with open(path, mode="r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            required_fields = {
                "dataset_id",
                "dataset_name",
                "version",
                "category",
                "language",
                "script",
                "file_path",
                "format",
                "encoding",
                "line_count",
                "character_count",
                "byte_size",
                "sha256_checksum",
                "license",
                "owner",
                "custodian",
                "authorization_status",
                "approval_ticket_id",
                "screening_status",
            }
            if reader.fieldnames is None or not required_fields.issubset(set(reader.fieldnames)):
                missing = required_fields - set(reader.fieldnames or [])
                raise ValueError(f"Inventory CSV missing required headers: {missing}")

            for row_num, row in enumerate(reader, start=2):
                try:
                    record = DatasetInventoryRecord(
                        dataset_id=row["dataset_id"].strip(),
                        dataset_name=row["dataset_name"].strip(),
                        version=row["version"].strip(),
                        category=row["category"].strip(),
                        language=row["language"].strip(),
                        script=row["script"].strip(),
                        file_path=row["file_path"].strip(),
                        format=row["format"].strip(),
                        encoding=row["encoding"].strip(),
                        line_count=int(row["line_count"]),
                        character_count=int(row["character_count"]),
                        byte_size=int(row["byte_size"]),
                        sha256_checksum=row["sha256_checksum"].strip(),
                        license=row["license"].strip(),
                        owner=row["owner"].strip(),
                        custodian=row["custodian"].strip(),
                        authorization_status=row["authorization_status"].strip(),
                        approval_ticket_id=row["approval_ticket_id"].strip(),
                        screening_status=row["screening_status"].strip(),
                    )
                    inventory.add_record(record)
                except Exception as ex:
                    raise ValueError(f"Error parsing row {row_num} in {csv_path}: {ex}") from ex

        return inventory

    def save_to_csv(self, csv_path: Union[str, Path]) -> None:
        path = Path(csv_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "dataset_id",
            "dataset_name",
            "version",
            "category",
            "language",
            "script",
            "file_path",
            "format",
            "encoding",
            "line_count",
            "character_count",
            "byte_size",
            "sha256_checksum",
            "license",
            "owner",
            "custodian",
            "authorization_status",
            "approval_ticket_id",
            "screening_status",
        ]
        with open(path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in self.records.values():
                writer.writerow(asdict(record))


def compute_file_metrics(file_path: Path) -> Dict[str, Any]:
    """Compute exact byte_size, line_count, character_count, and sha256 checksum."""
    h = hashlib.sha256()
    byte_count = 0
    line_count = 0
    char_count = 0

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
            byte_count += len(chunk)

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line_count += 1
            char_count += len(line)

    return {
        "byte_size": byte_count,
        "line_count": line_count,
        "character_count": char_count,
        "sha256": h.hexdigest(),
    }


def generate_manifest(
    target_dir: Union[str, Path],
    dataset_id: str,
    output_manifest_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Deterministically scan target directory and produce SHA-256 cryptographic manifest."""
    root_dir = Path(target_dir)
    if not root_dir.is_dir():
        raise NotADirectoryError(f"Target directory does not exist: {root_dir}")

    files_list: List[Dict[str, Any]] = []
    total_bytes = 0
    total_lines = 0
    total_chars = 0

    all_files = sorted([p for p in root_dir.rglob("*") if p.is_file()])

    for p in all_files:
        if p.name == "manifest.json":
            continue
        rel_path = p.relative_to(root_dir).as_posix()
        ext = p.suffix.lstrip(".").lower()
        metrics = compute_file_metrics(p)

        file_entry = {
            "relative_path": rel_path,
            "format": ext or "bin",
            "encoding": "UTF-8",
            "byte_size": metrics["byte_size"],
            "line_count": metrics["line_count"],
            "character_count": metrics["character_count"],
            "sha256": metrics["sha256"],
        }
        files_list.append(file_entry)
        total_bytes += metrics["byte_size"]
        total_lines += metrics["line_count"]
        total_chars += metrics["character_count"]

    manifest_content = {
        "manifest_version": "1.0.0",
        "dataset_id": dataset_id,
        "generated_at": "2026-11-17T09:00:00Z",
        "generator_tool": "scripts/dataset_inventory.py::generate_manifest",
        "root_directory": root_dir.name,
        "files": files_list,
        "total_files": len(files_list),
        "total_bytes": total_bytes,
        "total_lines": total_lines,
        "total_characters": total_chars,
    }

    raw_manifest_str = json.dumps(manifest_content, indent=2, sort_keys=True)
    manifest_hash = hashlib.sha256(raw_manifest_str.encode("utf-8")).hexdigest()
    manifest_content["manifest_sha256"] = manifest_hash

    if output_manifest_path:
        out_p = Path(output_manifest_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(manifest_content, f, indent=2, sort_keys=True)
            f.write("\n")

    return manifest_content


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="IGRIS Dataset Inventory Utility")
    parser.add_argument("--validate-csv", type=str, help="Validate an inventory CSV file")
    parser.add_argument("--check-authorized", type=str, help="Dataset ID to check for authorization in inventory CSV")
    parser.add_argument("--inventory-csv", type=str, help="Path to inventory CSV file for checks")
    parser.add_argument("--generate-manifest", type=str, help="Directory to scan")
    parser.add_argument("--dataset-id", type=str, help="Dataset ID for manifest")
    parser.add_argument("--out-manifest", type=str, help="Output manifest path")

    args = parser.parse_args()

    if args.check_authorized:
        csv_file = args.inventory_csv or args.validate_csv
        if not csv_file:
            print("Error: --inventory-csv or --validate-csv is required with --check-authorized")
            exit(1)
        inv = DatasetInventory.load_from_csv(csv_file)
        try:
            rec = inv.get_authorized_record(args.check_authorized)
            print(f"SUCCESS: Dataset '{rec.dataset_id}' is AUTHORIZED (APPROVED).")
            exit(0)
        except Exception as ex:
            print(f"DENIED: {ex}")
            exit(1)

    elif args.validate_csv:
        inv = DatasetInventory.load_from_csv(args.validate_csv)
        errs = inv.validate_inventory()
        if errs:
            print(f"FAILED: Found {len(errs)} inventory errors:")
            for err in errs:
                print(f"  - {err}")
            exit(1)
        else:
            print(f"SUCCESS: Validated {len(inv.records)} records in {args.validate_csv}")

    elif args.generate_manifest:
        if not args.dataset_id:
            print("Error: --dataset-id is required when generating a manifest")
            exit(1)
        mf = generate_manifest(args.generate_manifest, args.dataset_id, args.out_manifest)
        print(f"Manifest generated successfully. SHA-256: {mf['manifest_sha256']}")
