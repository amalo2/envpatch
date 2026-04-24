"""Stack multiple .env files by layering them in priority order."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envpatch.parser import parse_env_string


@dataclass
class StackResult:
    """Result of stacking multiple .env layers."""

    env: Dict[str, str]
    layers: List[str]
    overrides: Dict[str, List[str]]  # key -> list of layer names that defined it
    total_keys: int = 0
    override_count: int = 0

    @property
    def layer_count(self) -> int:
        return len(self.layers)

    def to_summary(self) -> str:
        lines = [
            f"Layers stacked : {self.layer_count}",
            f"Total keys     : {self.total_keys}",
            f"Overrides      : {self.override_count}",
        ]
        if self.overrides:
            lines.append("Override detail:")
            for key, sources in self.overrides.items():
                lines.append(f"  {key}: {' -> '.join(sources)}")
        return "\n".join(lines)


def stack_envs(
    layers: List[str],
    layer_names: Optional[List[str]] = None,
) -> StackResult:
    """Stack env strings in order; later layers override earlier ones.

    Args:
        layers: List of raw .env file contents, lowest to highest priority.
        layer_names: Optional human-readable names for each layer.

    Returns:
        StackResult with merged env and metadata.
    """
    if layer_names is None:
        layer_names = [f"layer{i}" for i in range(len(layers))]

    if len(layer_names) != len(layers):
        raise ValueError("layer_names length must match layers length")

    merged: Dict[str, str] = {}
    seen: Dict[str, List[str]] = {}  # key -> layers that defined it

    for name, content in zip(layer_names, layers):
        parsed = parse_env_string(content)
        for key, value in parsed.items():
            if key in merged:
                seen[key].append(name)
            else:
                seen[key] = [name]
            merged[key] = value

    overrides = {k: v for k, v in seen.items() if len(v) > 1}
    override_count = sum(len(v) - 1 for v in overrides.values())

    return StackResult(
        env=merged,
        layers=layer_names,
        overrides=overrides,
        total_keys=len(merged),
        override_count=override_count,
    )
