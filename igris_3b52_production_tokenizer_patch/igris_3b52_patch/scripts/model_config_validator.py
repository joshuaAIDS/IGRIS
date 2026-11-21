"""IGRIS Phase 16 — Model Configuration Validator.

Validates model configurations against architectural invariants and identifies
any discrepancies between baseline and production specifications.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# Setup patch paths
_PATCH_ROOT = Path(__file__).resolve().parents[1]
_PATCH_SRC = str(_PATCH_ROOT / "src")
_PATCH_SCRIPTS = str(_PATCH_ROOT / "scripts")
import sys
for p in [_PATCH_SRC, _PATCH_SCRIPTS]:
    if p not in sys.path:
        sys.path.insert(0, p)

from igris.model.transformer import (
    IgrisConfig,
    get_baseline_50m_config,
    get_production_config,
    get_test_tiny_config,
)

SCHEMA_PATH = _PATCH_ROOT / "MODEL_CONFIG_SCHEMA.json"


@dataclass
class ConfigValidationResult:
    is_valid: bool
    config_name: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    discrepancies: list[str] = field(default_factory=list)
    config_summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ModelConfigValidator:
    """Validates model configuration parameters and reconciles specifications."""

    def __init__(self, schema_file: Path | str | None = None):
        self.schema_path = Path(schema_file or SCHEMA_PATH)
        self.schema = json.loads(self.schema_path.read_text(encoding="utf-8"))

    def validate_config(self, config: IgrisConfig) -> ConfigValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        discrepancies: list[str] = []

        # 1. Vocab Size Invariant
        if config.vocab_size != 32768:
            errors.append(f"vocab_size must be exactly 32768 to match tokenizers; got {config.vocab_size}")

        # 2. Structural token IDs
        if config.pad_token_id != 0:
            errors.append(f"pad_token_id must be 0; got {config.pad_token_id}")
        if config.bos_token_id != 1:
            errors.append(f"bos_token_id must be 1; got {config.bos_token_id}")
        if config.eos_token_id != 2:
            errors.append(f"eos_token_id must be 2; got {config.eos_token_id}")

        # 3. Head Dimension Divisibility
        if config.hidden_size % config.num_attention_heads != 0:
            errors.append(
                f"hidden_size ({config.hidden_size}) must be divisible by num_attention_heads ({config.num_attention_heads})"
            )

        # 4. GQA Divisibility
        if config.num_attention_heads % config.num_key_value_heads != 0:
            errors.append(
                f"num_attention_heads ({config.num_attention_heads}) must be divisible by num_key_value_heads ({config.num_key_value_heads})"
            )

        # 5. Position Embeddings (Context Length)
        if config.max_position_embeddings > 2048:
            warnings.append(
                f"max_position_embeddings ({config.max_position_embeddings}) exceeds standard context window (2048)"
            )

        # 6. Check for specification discrepancies between baseline and production
        prod_ref = get_production_config()
        base_ref = get_baseline_50m_config()

        if config.num_hidden_layers != prod_ref.num_hidden_layers:
            discrepancies.append(
                f"Layer count ({config.num_hidden_layers}) differs from production target ({prod_ref.num_hidden_layers}). "
                f"Baseline specifies {base_ref.num_hidden_layers} layers."
            )
        if config.intermediate_size != prod_ref.intermediate_size:
            discrepancies.append(
                f"Intermediate dimension ({config.intermediate_size}) differs from production target ({prod_ref.intermediate_size}). "
                f"Baseline specifies {base_ref.intermediate_size}."
            )

        return ConfigValidationResult(
            is_valid=(len(errors) == 0),
            config_name=config.name,
            errors=errors,
            warnings=warnings,
            discrepancies=discrepancies,
            config_summary=config.to_dict(),
        )


if __name__ == "__main__":
    validator = ModelConfigValidator()
    print("=== Validating Production Target Configuration ===")
    res_prod = validator.validate_config(get_production_config())
    print(json.dumps(res_prod.to_dict(), indent=2))

    print("\n=== Validating Baseline 50M Configuration ===")
    res_base = validator.validate_config(get_baseline_50m_config())
    print(json.dumps(res_base.to_dict(), indent=2))
