"""Convert .env files to/from other formats (JSON, YAML, TOML)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, Optional

from envpatch.parser import parse_env_string


@dataclass
class ConvertResult:
    output: str
    fmt: str
    key_count: int
    warnings: list = field(default_factory=list)

    def to_summary(self) -> str:
        lines = [f"Format : {self.fmt}", f"Keys   : {self.key_count}"]
        if self.warnings:
            lines.append(f"Warnings: {len(self.warnings)}")
            for w in self.warnings:
                lines.append(f"  - {w}")
        return "\n".join(lines)


def _env_to_dict(env_string: str) -> Dict[str, str]:
    return parse_env_string(env_string)


def convert_env(env_string: str, fmt: str) -> ConvertResult:
    """Convert an env string to the given format ('json', 'yaml', 'toml')."""
    data = _env_to_dict(env_string)
    fmt = fmt.lower()
    warnings: list = []

    if fmt == "json":
        output = json.dumps(data, indent=2)
    elif fmt == "yaml":
        try:
            import yaml  # type: ignore
            output = yaml.dump(data, default_flow_style=False)
        except ImportError:
            warnings.append("PyYAML not installed; falling back to JSON")
            output = json.dumps(data, indent=2)
            fmt = "json"
    elif fmt == "toml":
        try:
            import tomli_w  # type: ignore
            output = tomli_w.dumps(data)
        except ImportError:
            warnings.append("tomli-w not installed; falling back to JSON")
            output = json.dumps(data, indent=2)
            fmt = "json"
    else:
        raise ValueError(f"Unsupported format: {fmt!r}. Choose json, yaml, or toml.")

    return ConvertResult(output=output, fmt=fmt, key_count=len(data), warnings=warnings)


def dict_to_env(data: Dict[str, str]) -> str:
    """Serialize a plain dict back to .env format."""
    lines = []
    for k, v in data.items():
        if any(c in v for c in (" ", "#", "'", '"')):
            v = f'"{v}"'
        lines.append(f"{k}={v}")
    return "\n".join(lines) + "\n"


def from_json(json_string: str) -> str:
    """Convert a JSON object string to .env format."""
    data = json.loads(json_string)
    if not isinstance(data, dict):
        raise ValueError("Top-level JSON value must be an object")
    return dict_to_env({str(k): str(v) for k, v in data.items()})
