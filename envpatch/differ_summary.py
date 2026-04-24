"""Summarizer for DiffResult objects — produces human-readable or structured summaries."""

from dataclasses import dataclass
from typing import Optional

from envpatch.differ import DiffResult


@dataclass
class DiffSummary:
    added: int
    removed: int
    modified: int
    unchanged: int
    total_changes: int
    has_changes: bool
    severity: str  # 'none', 'low', 'medium', 'high'

    def to_summary(self) -> str:
        if not self.has_changes:
            return "No changes detected."
        parts = []
        if self.added:
            parts.append(f"+{self.added} added")
        if self.removed:
            parts.append(f"-{self.removed} removed")
        if self.modified:
            parts.append(f"~{self.modified} modified")
        change_str = ", ".join(parts)
        return f"[{self.severity.upper()}] {change_str} ({self.total_changes} total change(s))"

    def to_dict(self) -> dict:
        return {
            "added": self.added,
            "removed": self.removed,
            "modified": self.modified,
            "unchanged": self.unchanged,
            "total_changes": self.total_changes,
            "has_changes": self.has_changes,
            "severity": self.severity,
        }


def _compute_severity(added: int, removed: int, modified: int) -> str:
    total = added + removed + modified
    if total == 0:
        return "none"
    if removed > 0 or total >= 10:
        return "high"
    if modified > 0 or total >= 5:
        return "medium"
    return "low"


def summarize_diff(diff: DiffResult, include_unchanged: bool = False) -> DiffSummary:
    """Produce a DiffSummary from a DiffResult."""
    added = len(diff.added)
    removed = len(diff.removed)
    modified = len(diff.modified)
    unchanged = len(diff.unchanged) if include_unchanged else len(diff.unchanged)
    total_changes = added + removed + modified
    has_changes = total_changes > 0
    severity = _compute_severity(added, removed, modified)
    return DiffSummary(
        added=added,
        removed=removed,
        modified=modified,
        unchanged=unchanged,
        total_changes=total_changes,
        has_changes=has_changes,
        severity=severity,
    )
