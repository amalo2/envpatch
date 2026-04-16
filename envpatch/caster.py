from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CastResult:
    cast: Dict[str, Any] = field(default_factory=dict)
    failed: List[str] = field(default_factory=list)
    fmt: str = "env"

    @property
    def cast_count(self) -> int:
        return len(self.cast)

    @property
    def failed_count(self) -> int:
        return len(self.failed)

    def to_summary(self) -> str:
        return (
            f"Cast {self.cast_count} keys, {self.failed_count} failed."
        )


def _cast_value(value: str) -> Any:
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip('"').strip("'") for item in inner.split(",")]
    return value


def cast_env(env: Dict[str, str], keys: List[str] | None = None) -> CastResult:
    """Cast env string values to native Python types."""
    result = CastResult()
    for key, raw in env.items():
        if keys and key not in keys:
            result.cast[key] = raw
            continue
        try:
            result.cast[key] = _cast_value(raw)
        except Exception:
            result.failed.append(key)
            result.cast[key] = raw
    return result
