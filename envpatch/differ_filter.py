"""Filter DiffResult changes by type, key pattern, or severity."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from envpatch.differ import DiffResult, EnvChange


@dataclass
class FilterResult:
    matched: List[EnvChange] = field(default_factory=list)
    excluded: List[EnvChange] = field(default_factory=list)
    filter_pattern: Optional[str] = None
    change_types: Optional[List[str]] = None

    @property
    def matched_count(self) -> int:
        return len(self.matched)

    @property
    def excluded_count(self) -> int:
        return len(self.excluded)

    def to_summary(self) -> str:
        parts = [f"matched={self.matched_count}", f"excluded={self.excluded_count}"]
        if self.filter_pattern:
            parts.append(f"pattern={self.filter_pattern!r}")
        if self.change_types:
            parts.append(f"types={','.join(self.change_types)}")
        return " ".join(parts)


def filter_diff(
    diff: DiffResult,
    *,
    pattern: Optional[str] = None,
    change_types: Optional[List[str]] = None,
    include_unchanged: bool = False,
) -> FilterResult:
    """Filter a DiffResult down to a subset of changes.

    Args:
        diff: The DiffResult to filter.
        pattern: Optional regex pattern matched against key names.
        change_types: Optional list of change types to include
                      (e.g. ["added", "removed", "modified"]).
        include_unchanged: Whether to include unchanged entries.

    Returns:
        FilterResult with matched and excluded change lists.
    """
    compiled = re.compile(pattern) if pattern else None
    allowed_types = set(change_types) if change_types else None

    all_changes = list(diff.changes)
    if include_unchanged:
        all_changes += list(diff.unchanged)

    matched: List[EnvChange] = []
    excluded: List[EnvChange] = []

    for change in all_changes:
        type_ok = allowed_types is None or change.change_type in allowed_types
        key_ok = compiled is None or compiled.search(change.key) is not None
        if type_ok and key_ok:
            matched.append(change)
        else:
            excluded.append(change)

    return FilterResult(
        matched=matched,
        excluded=excluded,
        filter_pattern=pattern,
        change_types=change_types,
    )
