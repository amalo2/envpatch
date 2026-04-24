"""Split a .env file into multiple files based on key prefixes or groups."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envpatch.parser import parse_env_string


@dataclass
class SplitResult:
    """Result of splitting a .env file into segments."""

    segments: Dict[str, Dict[str, str]] = field(default_factory=dict)
    unmatched: Dict[str, str] = field(default_factory=dict)

    @property
    def segment_count(self) -> int:
        return len(self.segments)

    @property
    def total_keys(self) -> int:
        total = sum(len(v) for v in self.segments.values())
        return total + len(self.unmatched)

    def to_summary(self) -> str:
        lines = [f"Segments: {self.segment_count}, Total keys: {self.total_keys}"]
        for name, keys in self.segments.items():
            lines.append(f"  [{name}]: {len(keys)} key(s)")
        if self.unmatched:
            lines.append(f"  [unmatched]: {len(self.unmatched)} key(s)")
        return "\n".join(lines)


def split_env(
    env_string: str,
    prefixes: List[str],
    *,
    strip_prefix: bool = False,
    keep_unmatched: bool = True,
) -> SplitResult:
    """Split parsed env keys into named segments by prefix.

    Args:
        env_string: Raw .env file content.
        prefixes: List of prefixes to split on (e.g. ["DB_", "AWS_"]).
        strip_prefix: If True, remove the matched prefix from keys in the segment.
        keep_unmatched: If True, unmatched keys are stored in result.unmatched.

    Returns:
        SplitResult with segments and optionally unmatched keys.
    """
    env = parse_env_string(env_string)
    result = SplitResult()

    for prefix in prefixes:
        result.segments[prefix] = {}

    for key, value in env.items():
        matched = False
        for prefix in prefixes:
            if key.startswith(prefix):
                out_key = key[len(prefix):] if strip_prefix else key
                result.segments[prefix][out_key] = value
                matched = True
                break
        if not matched and keep_unmatched:
            result.unmatched[key] = value

    return result
