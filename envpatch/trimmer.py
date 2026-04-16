"""Trim whitespace from .env values."""
from dataclasses import dataclass, field
from typing import Dict, List
from envpatch.parser import parse_env_string
from envpatch.patcher import serialize_env


@dataclass
class TrimResult:
    output: str
    trimmed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def trimmed_count(self) -> int:
        return len(self.trimmed)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def to_summary(self) -> str:
        return (
            f"Trimmed {self.trimmed_count} key(s), "
            f"{self.skipped_count} already clean."
        )


def trim_env(source: str, keys: List[str] = None) -> TrimResult:
    """Trim leading/trailing whitespace from env values.

    Args:
        source: Raw .env file content.
        keys: Optional list of keys to trim. If None, all keys are trimmed.

    Returns:
        TrimResult with updated env content and lists of affected keys.
    """
    parsed: Dict[str, str] = parse_env_string(source)
    output: Dict[str, str] = {}
    trimmed: List[str] = []
    skipped: List[str] = []

    for key, value in parsed.items():
        if keys is not None and key not in keys:
            output[key] = value
            continue
        stripped = value.strip()
        if stripped != value:
            output[key] = stripped
            trimmed.append(key)
        else:
            output[key] = value
            skipped.append(key)

    return TrimResult(
        output=serialize_env(output),
        trimmed=trimmed,
        skipped=skipped,
    )
