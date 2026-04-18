"""Normalize .env keys: uppercase, strip whitespace, replace hyphens with underscores."""
from dataclasses import dataclass, field
from typing import Dict, List

from envpatch.parser import parse_env_string


@dataclass
class NormalizeResult:
    output: Dict[str, str]
    normalized: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def normalized_count(self) -> int:
        return len(self.normalized)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def to_summary(self) -> str:
        return (
            f"Normalized: {self.normalized_count} key(s), "
            f"unchanged: {self.skipped_count} key(s)."
        )


def _normalize_key(key: str) -> str:
    return key.strip().upper().replace("-", "_")


def normalize_env(env_string: str) -> NormalizeResult:
    """Parse env_string and normalize all keys."""
    parsed = parse_env_string(env_string)
    output: Dict[str, str] = {}
    normalized: List[str] = []
    skipped: List[str] = []

    for key, value in parsed.items():
        new_key = _normalize_key(key)
        output[new_key] = value
        if new_key != key:
            normalized.append(key)
        else:
            skipped.append(key)

    return NormalizeResult(output=output, normalized=normalized, skipped=skipped)
