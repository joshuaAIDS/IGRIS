"""IGRIS Training Package — Production Training Engine, MMap Datasets, and Checkpointing."""

from igris.training.dataset import (
    BinaryDatasetWriter,
    DatasetIntegrityError,
    DatasetManifest,
    MMapDataset,
    SequencePacker,
    SplitIsolationError,
    StreamingDatasetLoader,
    compute_file_sha256,
)
from igris.training.evaluator import (
    EvaluationMetrics,
    IgrisEvaluator,
)
from igris.training.checkpoint import (
    CheckpointCorruptionError,
    CheckpointError,
    CheckpointMetadata,
    IgrisCheckpointManager,
    IncompatibleArchitectureError,
    IncompatibleTokenizerError,
    compute_config_fingerprint,
)
from igris.training.engine import (
    IgrisTrainer,
    TrainingConfig,
)

__all__ = [
    "BinaryDatasetWriter",
    "DatasetIntegrityError",
    "DatasetManifest",
    "MMapDataset",
    "SequencePacker",
    "SplitIsolationError",
    "StreamingDatasetLoader",
    "compute_file_sha256",
    "EvaluationMetrics",
    "IgrisEvaluator",
    "CheckpointCorruptionError",
    "CheckpointError",
    "CheckpointMetadata",
    "IgrisCheckpointManager",
    "IncompatibleArchitectureError",
    "IncompatibleTokenizerError",
    "compute_config_fingerprint",
    "IgrisTrainer",
    "TrainingConfig",
]
