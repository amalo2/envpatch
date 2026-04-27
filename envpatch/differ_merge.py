"""Merge two DiffResults into a single consolidated DiffResult."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envpatch.differ import DiffResult, EnvChange


@dataclass
class MergeDiffResult:
    """Result of merging two DiffResults together."""

    changes: List[EnvChange] = field(default_factory=list)
    conflict_keys: List[str] = field(default_factory=list)
    source_a_only: List[str] = field(default_factory=list)
    source_b_only: List[str] = field(default_factory=list)

    @property
    def conflict_count(self) -> int:
        return len(self.conflict_keys)

    @property
    def has_conflicts(self) -> bool:
        return self.conflict_count > 0

    def to_summary(self) -> str:
        lines = [
            f"Merged changes : {len(self.changes)}",
            f"Conflicts      : {self.conflict_count}",
            f"Only in A      : {len(self.source_a_only)}",
            f"Only in B      : {len(self.source_b_only)}",
        ]
        if self.conflict_keys:
            lines.append("Conflict keys  : " + ", ".join(self.conflict_keys))
        return "\n".join(lines)


def merge_diffs(
    diff_a: DiffResult,
    diff_b: DiffResult,
    prefer: str = "b",
) -> MergeDiffResult:
    """Merge two DiffResults.

    When the same key appears in both diffs with *different* new_value,
    the key is recorded as a conflict. The ``prefer`` argument controls
    which side wins: ``"a"`` or ``"b"`` (default).

    Parameters
    ----------
    diff_a:
        First diff (lower priority by default).
    diff_b:
        Second diff (higher priority by default).
    prefer:
        Which side wins on conflict – ``"a"`` or ``"b"``.
    """
    if prefer not in ("a", "b"):
        raise ValueError("prefer must be 'a' or 'b'")

    index_a: dict[str, EnvChange] = {c.key: c for c in diff_a.changes}
    index_b: dict[str, EnvChange] = {c.key: c for c in diff_b.changes}

    result = MergeDiffResult()
    all_keys = set(index_a) | set(index_b)

    for key in sorted(all_keys):
        in_a = key in index_a
        in_b = key in index_b

        if in_a and not in_b:
            result.changes.append(index_a[key])
            result.source_a_only.append(key)
        elif in_b and not in_a:
            result.changes.append(index_b[key])
            result.source_b_only.append(key)
        else:
            change_a = index_a[key]
            change_b = index_b[key]
            if change_a.new_value != change_b.new_value:
                result.conflict_keys.append(key)
                winner = change_b if prefer == "b" else change_a
            else:
                winner = change_b
            result.changes.append(winner)

    return result
