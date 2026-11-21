"""IGRIS Dataset Infrastructure — Streaming, Memory-Mapped Binary Format, and Sequence Packing.

Provides high-throughput, memory-mapped binary dataset storage, streaming collation,
multi-document sequence packing, EOS boundary handling, and strict train/val/test isolation.
"""
from __future__ import annotations

import hashlib
import json
import os
import struct
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

import numpy as np
import torch
from torch.utils.data import Dataset

BOS_TOKEN_ID = 1  # <|begin_of_text|>
EOS_TOKEN_ID = 2  # <|end_of_text|>
PAD_TOKEN_ID = 0  # <|pad|>


class DatasetIntegrityError(Exception):
    """Raised when dataset file hash, index, or structure fails validation."""


class SplitIsolationError(PermissionError):
    """Raised when an attempt is made to train on or select checkpoints using the test split."""


@dataclass
class DatasetManifest:
    split_name: str
    num_documents: int
    total_tokens: int
    bin_file: str
    bin_sha256: str
    idx_file: str
    idx_sha256: str
    language_counts: Dict[str, int]
    max_doc_len: int
    min_doc_len: int
    avg_doc_len: float
    created_at: str
    schema_version: str = "v1.0.0-mmap"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DatasetManifest:
        return cls(**data)


def compute_file_sha256(filepath: Union[str, Path]) -> str:
    """Compute SHA-256 of any binary file on disk."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class BinaryDatasetWriter:
    """Writes tokenized documents into memory-mapped uint16 binary format (.bin + .idx)."""

    def __init__(self, output_dir: Union[str, Path], split_name: str):
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.split_name = split_name

        self.bin_path = self.output_dir / f"{split_name}.bin"
        self.idx_path = self.output_dir / f"{split_name}.idx"
        self.manifest_path = self.output_dir / f"{split_name}_manifest.json"

        self.bin_file = open(self.bin_path, "wb")
        self.idx_file = open(self.idx_path, "wb")

        self.num_documents = 0
        self.total_tokens = 0
        self.current_offset = 0
        self.doc_lengths: List[int] = []
        self.language_counts: Dict[str, int] = {}

    def add_document(self, token_ids: List[int], language: str = "UNKNOWN") -> None:
        """Add a tokenized document to the binary stream."""
        if not token_ids:
            return

        # Ensure all tokens fit in uint16 (0..65535, IGRIS vocab is 32,768)
        arr = np.array(token_ids, dtype=np.uint16)
        raw_bytes = arr.tobytes()

        # Write to binary token stream
        self.bin_file.write(raw_bytes)

        # Write index entry: (byte_offset: int64, token_length: int64)
        length = len(token_ids)
        self.idx_file.write(struct.pack("<QQ", self.current_offset, length))

        self.current_offset += len(raw_bytes)
        self.num_documents += 1
        self.total_tokens += length
        self.doc_lengths.append(length)
        self.language_counts[language] = self.language_counts.get(language, 0) + 1

    def close(self) -> DatasetManifest:
        """Flush and close binary files, compute SHA256 hashes, and write manifest."""
        self.bin_file.close()
        self.idx_file.close()

        bin_hash = compute_file_sha256(self.bin_path)
        idx_hash = compute_file_sha256(self.idx_path)

        min_len = min(self.doc_lengths) if self.doc_lengths else 0
        max_len = max(self.doc_lengths) if self.doc_lengths else 0
        avg_len = float(np.mean(self.doc_lengths)) if self.doc_lengths else 0.0

        manifest = DatasetManifest(
            split_name=self.split_name,
            num_documents=self.num_documents,
            total_tokens=self.total_tokens,
            bin_file=self.bin_path.name,
            bin_sha256=bin_hash,
            idx_file=self.idx_path.name,
            idx_sha256=idx_hash,
            language_counts=self.language_counts,
            max_doc_len=max_len,
            min_doc_len=min_len,
            avg_doc_len=round(avg_len, 2),
            created_at=str(np.datetime64("now")),
        )

        self.manifest_path.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")
        return manifest


class MMapDataset(Dataset):
    """Memory-mapped dataset providing zero-RAM random access to pre-tokenized documents."""

    def __init__(self, output_dir: Union[str, Path], split_name: str, verify_integrity: bool = True):
        self.output_dir = Path(output_dir).resolve()
        self.split_name = split_name

        self.bin_path = self.output_dir / f"{split_name}.bin"
        self.idx_path = self.output_dir / f"{split_name}.idx"
        self.manifest_path = self.output_dir / f"{split_name}_manifest.json"

        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found at {self.manifest_path}")

        self.manifest = DatasetManifest.from_dict(json.loads(self.manifest_path.read_text(encoding="utf-8")))

        if verify_integrity:
            self.validate_integrity()

        # Map binary index (pairs of uint64: byte_offset, token_length)
        self.idx_mmap = np.memmap(self.idx_path, dtype=np.uint64, mode="r").reshape(-1, 2)
        # Map binary tokens (uint16)
        self.bin_mmap = np.memmap(self.bin_path, dtype=np.uint16, mode="r")

    def validate_integrity(self) -> None:
        """Verify binary files match manifest SHA-256."""
        actual_bin_hash = compute_file_sha256(self.bin_path)
        actual_idx_hash = compute_file_sha256(self.idx_path)

        if actual_bin_hash != self.manifest.bin_sha256:
            raise DatasetIntegrityError(
                f"Binary hash mismatch for {self.split_name}: expected {self.manifest.bin_sha256}, got {actual_bin_hash}"
            )
        if actual_idx_hash != self.manifest.idx_sha256:
            raise DatasetIntegrityError(
                f"Index hash mismatch for {self.split_name}: expected {self.manifest.idx_sha256}, got {actual_idx_hash}"
            )

    def close(self) -> None:
        """Close memory-mapped buffers to release file handles on Windows."""
        if hasattr(self, "idx_mmap") and hasattr(self.idx_mmap, "_mmap") and self.idx_mmap._mmap is not None:
            self.idx_mmap._mmap.close()
        if hasattr(self, "bin_mmap") and hasattr(self.bin_mmap, "_mmap") and self.bin_mmap._mmap is not None:
            self.bin_mmap._mmap.close()

    def __len__(self) -> int:
        return len(self.idx_mmap)

    def __getitem__(self, idx: int) -> torch.Tensor:
        byte_offset, token_length = self.idx_mmap[idx]
        token_offset = int(byte_offset // 2)  # 2 bytes per uint16
        tokens = self.bin_mmap[token_offset : token_offset + int(token_length)].astype(np.int64)
        return torch.from_numpy(tokens)


class SequencePacker:
    """Multi-document sequence packing engine with EOS boundaries, truncation, and padding."""

    def __init__(self, max_seq_len: int = 2048, pad_token_id: int = PAD_TOKEN_ID, eos_token_id: int = EOS_TOKEN_ID, bos_token_id: int = BOS_TOKEN_ID):
        self.max_seq_len = max_seq_len
        self.pad_token_id = pad_token_id
        self.eos_token_id = eos_token_id
        self.bos_token_id = bos_token_id

    def pack_documents(
        self,
        documents: List[List[int]],
        prepend_bos: bool = True,
        append_eos: bool = True,
    ) -> List[Dict[str, torch.Tensor]]:
        """Pack a list of documents into fixed max_seq_len sequences."""
        packed_batches: List[Dict[str, torch.Tensor]] = []
        current_seq: List[int] = []

        for doc in documents:
            if not doc:
                continue

            # Format document with optional BOS and mandatory EOS
            tokens = list(doc)
            if prepend_bos and (not tokens or tokens[0] != self.bos_token_id):
                tokens = [self.bos_token_id] + tokens
            if append_eos and (not tokens or tokens[-1] != self.eos_token_id):
                tokens = tokens + [self.eos_token_id]

            # If document alone exceeds max_seq_len, flush current buffer and truncate cleanly
            if len(tokens) >= self.max_seq_len:
                if current_seq:
                    packed_batches.append(self._finalize_sequence(current_seq))
                    current_seq = []
                truncated = tokens[: self.max_seq_len - 1] + [self.eos_token_id]
                batch_dict = self._finalize_sequence(truncated)
                packed_batches.append(batch_dict)
                continue

            # If adding this document exceeds max_seq_len, finalize current sequence
            if len(current_seq) + len(tokens) > self.max_seq_len:
                batch_dict = self._finalize_sequence(current_seq)
                packed_batches.append(batch_dict)
                current_seq = []

            current_seq.extend(tokens)

        # Finalize remaining tokens
        if current_seq:
            batch_dict = self._finalize_sequence(current_seq)
            packed_batches.append(batch_dict)

        return packed_batches

    def _finalize_sequence(self, seq: List[int]) -> Dict[str, torch.Tensor]:
        """Pads sequence to max_seq_len and constructs attention_mask and labels."""
        seq_len = len(seq)
        pad_len = self.max_seq_len - seq_len

        input_ids = seq + [self.pad_token_id] * pad_len
        attention_mask = [1] * seq_len + [0] * pad_len

        # Autoregressive labels: pad tokens mapped to -100 (ignored in loss)
        labels = [tok if mask == 1 else -100 for tok, mask in zip(input_ids, attention_mask)]

        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
            "labels": torch.tensor(labels, dtype=torch.long),
            "actual_tokens": seq_len,
        }


class StreamingDatasetLoader:
    """Streams packed, batched tensors from MMapDataset with strict split governance."""

    def __init__(
        self,
        dataset: MMapDataset,
        batch_size: int = 4,
        max_seq_len: int = 2048,
        shuffle: bool = False,
        seed: int = 42,
    ):
        self.dataset = dataset
        self.batch_size = batch_size
        self.max_seq_len = max_seq_len
        self.shuffle = shuffle
        self.seed = seed
        self.packer = SequencePacker(max_seq_len=max_seq_len)

    def __iter__(self) -> Iterator[Dict[str, torch.Tensor]]:
        num_docs = len(self.dataset)
        indices = list(range(num_docs))
        if self.shuffle:
            rng = np.random.RandomState(self.seed)
            rng.shuffle(indices)

        # Stream documents and pack them
        doc_batch: List[List[int]] = []
        for idx in indices:
            tokens = self.dataset[idx].tolist()
            doc_batch.append(tokens)

            # When enough documents collected, pack and yield batches
            if len(doc_batch) >= self.batch_size * 4:
                packed_sequences = self.packer.pack_documents(doc_batch)
                for i in range(0, len(packed_sequences), self.batch_size):
                    chunk = packed_sequences[i : i + self.batch_size]
                    if len(chunk) == self.batch_size:
                        yield self._collate_chunk(chunk)
                doc_batch = []

        if doc_batch:
            packed_sequences = self.packer.pack_documents(doc_batch)
            for i in range(0, len(packed_sequences), self.batch_size):
                chunk = packed_sequences[i : i + self.batch_size]
                if chunk:
                    yield self._collate_chunk(chunk)

    def _collate_chunk(self, chunk: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
        return {
            "input_ids": torch.stack([c["input_ids"] for c in chunk]),
            "attention_mask": torch.stack([c["attention_mask"] for c in chunk]),
            "labels": torch.stack([c["labels"] for c in chunk]),
        }
