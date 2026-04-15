"""Merge .env files by applying new keys without overwriting existing ones."""

from typing import Dict, Optional, List
from dataclasses import dataclass, field

from envpatch.parser import parse_env_string
from envpatch.differ import DiffResult, EnvChange


@dataclass
class MergeResult:
    """Result of merging two env configurations."""
    merged: Dict[str, str]
    applied: List[EnvChange] = field(default_factory=list)
    skipped: List[EnvChange] = field(default_factory=list)

    @property
    def applied_count(self) -> int:
        return len(self.applied)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def to_summary(self) -> str:
        lines = []
        if self.applied:
            lines.append(f"Applied ({self.applied_count}):")
            for change in self.applied:
                lines.append(f"  + {change.key}={change.new_value}")
        if self.skipped:
            lines.append(f"Skipped ({self.skipped_count}):")
            for change in self.skipped:
                lines.append(f"  ~ {change.key} (kept existing value)")
        if not lines:
            lines.append("No changes applied.")
        return "\n".join(lines)


def merge_envs(
    base: Dict[str, str],
    incoming: Dict[str, str],
    overwrite: bool = False,
    keys: Optional[List[str]] = None,
) -> MergeResult:
    """Merge incoming env vars into base without overwriting existing keys.

    Args:
        base: The existing environment variables.
        incoming: New environment variables to merge in.
        overwrite: If True, overwrite existing keys with incoming values.
        keys: Optional list of specific keys to merge; merges all if None.

    Returns:
        MergeResult with merged dict and change tracking.
    """
    merged = dict(base)
    applied: List[EnvChange] = []
    skipped: List[EnvChange] = []

    candidates = {k: v for k, v in incoming.items() if keys is None or k in (keys or [])}

    for key, new_value in candidates.items():
        old_value = base.get(key)
        change = EnvChange(key=key, old_value=old_value, new_value=new_value)

        if key in base and not overwrite:
            skipped.append(change)
        else:
            merged[key] = new_value
            applied.append(change)

    return MergeResult(merged=merged, applied=applied, skipped=skipped)


def merge_env_strings(
    base_str: str,
    incoming_str: str,
    overwrite: bool = False,
    keys: Optional[List[str]] = None,
) -> MergeResult:
    """Parse two env strings and merge them."""
    base = parse_env_string(base_str)
    incoming = parse_env_string(incoming_str)
    return merge_envs(base, incoming, overwrite=overwrite, keys=keys)
