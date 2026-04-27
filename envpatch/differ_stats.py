"""Compute statistical metrics from a DiffResult."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envpatch.differ import DiffResult


@dataclass
class DiffStats:
    """Aggregated statistics derived from a DiffResult."""

    total_changes: int = 0
    added_count: int = 0
    removed_count: int = 0
    modified_count: int = 0
    change_ratio: float = 0.0  # changed keys / total keys seen
    most_changed_keys: List[str] = field(default_factory=list)
    change_type_breakdown: Dict[str, int] = field(default_factory=dict)

    # ------------------------------------------------------------------ #
    # Derived helpers
    # ------------------------------------------------------------------ #

    @property
    def has_changes(self) -> bool:
        return self.total_changes > 0

    def to_summary(self) -> str:
        lines = [
            f"Total changes : {self.total_changes}",
            f"  Added       : {self.added_count}",
            f"  Removed     : {self.removed_count}",
            f"  Modified    : {self.modified_count}",
            f"Change ratio  : {self.change_ratio:.1%}",
        ]
        if self.most_changed_keys:
            keys_str = ", ".join(self.most_changed_keys[:5])
            lines.append(f"Top keys      : {keys_str}")
        return "\n".join(lines)

    def to_dict(self) -> Dict:
        return {
            "total_changes": self.total_changes,
            "added_count": self.added_count,
            "removed_count": self.removed_count,
            "modified_count": self.modified_count,
            "change_ratio": round(self.change_ratio, 4),
            "most_changed_keys": self.most_changed_keys,
            "change_type_breakdown": self.change_type_breakdown,
        }


def compute_stats(diff: DiffResult, total_key_universe: int = 0) -> DiffStats:
    """Return a DiffStats for *diff*.

    Args:
        diff: A DiffResult produced by envpatch.differ.
        total_key_universe: Optional hint for the total number of keys across
            both files (used to compute change_ratio).  When 0 the union of
            all seen keys is used instead.
    """
    added = list(diff.added)
    removed = list(diff.removed)
    modified = list(diff.modified)

    total_changes = len(added) + len(removed) + len(modified)

    # Build a universe of key names for the ratio denominator.
    all_keys: set = set()
    for change in diff.changes:
        all_keys.add(change.key)
    universe = total_key_universe if total_key_universe > 0 else max(len(all_keys), 1)

    change_ratio = total_changes / universe

    # Most-changed keys ordered by change type priority: modified > removed > added.
    ordered: List[str] = (
        [c.key for c in modified]
        + [c.key for c in removed]
        + [c.key for c in added]
    )

    breakdown: Dict[str, int] = {}
    for change in diff.changes:
        breakdown[change.change_type] = breakdown.get(change.change_type, 0) + 1

    return DiffStats(
        total_changes=total_changes,
        added_count=len(added),
        removed_count=len(removed),
        modified_count=len(modified),
        change_ratio=min(change_ratio, 1.0),
        most_changed_keys=ordered,
        change_type_breakdown=breakdown,
    )
