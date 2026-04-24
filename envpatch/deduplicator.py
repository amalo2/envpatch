"""Deduplicator: resolve duplicate keys in an .env string, keeping first or last occurrence."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envpatch.parser import parse_env_string


@dataclass
class DeduplicateResult:
    env: Dict[str, str]
    resolved: List[str] = field(default_factory=list)
    kept_lines: Dict[str, int] = field(default_factory=dict)  # key -> 1-based line number kept

    @property
    def resolved_count(self) -> int:
        return len(self.resolved)

    @property
    def clean(self) -> bool:
        return self.resolved_count == 0

    def to_summary(self) -> str:
        if self.clean:
            return "No duplicate keys found."
        keys = ", ".join(self.resolved)
        return f"Resolved {self.resolved_count} duplicate key(s): {keys}"


def deduplicate_env(
    env_string: str,
    keep: str = "last",
) -> DeduplicateResult:
    """Deduplicate keys in *env_string*.

    Args:
        env_string: Raw .env file contents.
        keep: ``"first"`` keeps the first occurrence; ``"last"`` (default) keeps the last.

    Returns:
        :class:`DeduplicateResult` with the resolved env dict and metadata.
    """
    if keep not in ("first", "last"):
        raise ValueError(f"keep must be 'first' or 'last', got {keep!r}")

    seen: Dict[str, List[int]] = {}  # key -> list of 1-based line numbers
    ordered: List[tuple[int, str, str]] = []  # (line_no, key, value)

    for lineno, line in enumerate(env_string.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, raw_val = stripped.partition("=")
        key = key.strip()
        if not key:
            continue
        seen.setdefault(key, [])
        seen[key].append(lineno)
        ordered.append((lineno, key, raw_val.strip()))

    duplicated_keys = {k for k, lines in seen.items() if len(lines) > 1}

    env: Dict[str, str] = {}
    kept_lines: Dict[str, int] = {}
    resolved: List[str] = []

    if keep == "first":
        for lineno, key, value in ordered:
            if key not in env:
                env[key] = _strip_quotes(value)
                kept_lines[key] = lineno
    else:  # last
        for lineno, key, value in ordered:
            env[key] = _strip_quotes(value)
            kept_lines[key] = lineno

    for key in duplicated_keys:
        resolved.append(key)

    resolved.sort()
    return DeduplicateResult(env=env, resolved=resolved, kept_lines=kept_lines)


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value
