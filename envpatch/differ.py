"""Diff two parsed .env dictionaries and produce a structured changeset."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EnvChange:
    """Represents a single key-level change between two .env states."""

    key: str
    change_type: str  # 'added' | 'removed' | 'modified' | 'unchanged'
    old_value: Optional[str] = None
    new_value: Optional[str] = None

    def __str__(self) -> str:
        if self.change_type == "added":
            return f"+ {self.key}={self.new_value}"
        if self.change_type == "removed":
            return f"- {self.key}={self.old_value}"
        if self.change_type == "modified":
            return f"~ {self.key}: {self.old_value!r} -> {self.new_value!r}"
        return f"  {self.key}={self.old_value}"


@dataclass
class DiffResult:
    """Collection of changes produced by diffing two env dicts."""

    changes: List[EnvChange] = field(default_factory=list)

    @property
    def added(self) -> List[EnvChange]:
        return [c for c in self.changes if c.change_type == "added"]

    @property
    def removed(self) -> List[EnvChange]:
        return [c for c in self.changes if c.change_type == "removed"]

    @property
    def modified(self) -> List[EnvChange]:
        return [c for c in self.changes if c.change_type == "modified"]

    @property
    def unchanged(self) -> List[EnvChange]:
        return [c for c in self.changes if c.change_type == "unchanged"]

    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.modified)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)} added")
        if self.removed:
            parts.append(f"-{len(self.removed)} removed")
        if self.modified:
            parts.append(f"~{len(self.modified)} modified")
        return ", ".join(parts) if parts else "no changes"


def diff_envs(
    base:
    target: Dict[str, str],
    include_unchanged: bool = False,
) -> DiffResult:
    """Diff *base* against *target* and return a :class:`DiffResult`.

    Args:
        base: The existing / current env mapping.
        target: The desired / patch env mapping.
        include_unchanged: When True, unchanged keys are included in the result.

    Returns:
        A :class:`DiffResult` describing every key-level change.
    """
    result = DiffResult()
    all_keys = sorted(set(base) | set(target))

    for key in all_keys:
        in_base = key in base
        in_target = key in target

        if in_base and in_target:
            if base[key] != target[key]:
                result.changes.append(
                    EnvChange(key, "modified", old_value=base[key], new_value=target[key])
                )
            elif include_unchanged:
                result.changes.append(
                    EnvChange(key, "unchanged", old_value=base[key], new_value=target[key])
                )
        elif in_target:
            result.changes.append(
                EnvChange(key, "added", new_value=target[key])
            )
        else:
            result.changes.append(
                EnvChange(key, "removed", old_value=base[key])
            )

    return result
