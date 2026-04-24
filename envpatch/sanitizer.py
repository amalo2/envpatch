"""Sanitize .env values by removing or replacing unsafe characters."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envpatch.parser import parse_env_string

_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_NULL_RE = re.compile(r"\x00")


@dataclass
class SanitizeResult:
    env: Dict[str, str]
    sanitized: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def sanitized_count(self) -> int:
        return len(self.sanitized)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def to_summary(self) -> str:
        return (
            f"Sanitized {self.sanitized_count} key(s), "
            f"{self.skipped_count} already clean."
        )


def _sanitize_value(value: str, replacement: str = "") -> tuple[str, bool]:
    """Remove control characters from value. Returns (clean_value, was_changed)."""
    cleaned = _CONTROL_RE.sub(replacement, value)
    cleaned = _NULL_RE.sub(replacement, cleaned)
    return cleaned, cleaned != value


def sanitize_env(
    source: str,
    keys: Optional[List[str]] = None,
    replacement: str = "",
) -> SanitizeResult:
    """Sanitize values in a .env string.

    Args:
        source: Raw .env file contents.
        keys: Optional list of keys to sanitize. If None, all keys are processed.
        replacement: String to replace unsafe characters with (default: remove).

    Returns:
        SanitizeResult with cleaned env dict and lists of affected keys.
    """
    parsed = parse_env_string(source)
    result_env: Dict[str, str] = {}
    sanitized: List[str] = []
    skipped: List[str] = []

    for key, value in parsed.items():
        if keys is not None and key not in keys:
            result_env[key] = value
            skipped.append(key)
            continue

        cleaned, changed = _sanitize_value(value, replacement)
        result_env[key] = cleaned
        if changed:
            sanitized.append(key)
        else:
            skipped.append(key)

    return SanitizeResult(env=result_env, sanitized=sanitized, skipped=skipped)
