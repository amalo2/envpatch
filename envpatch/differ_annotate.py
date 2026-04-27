"""Annotation layer for env diffs.

Attaches human-readable notes, severity labels, and contextual hints
to individual EnvChange entries in a DiffResult.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envpatch.differ import DiffResult, EnvChange
from envpatch.redactor import is_sensitive


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Annotation:
    """A single annotation attached to an EnvChange."""

    key: str
    change_type: str          # 'added' | 'removed' | 'modified'
    severity: str             # 'info' | 'warning' | 'critical'
    note: str                 # Human-readable description
    hints: List[str] = field(default_factory=list)
    sensitive: bool = False

    def to_dict(self) -> Dict:
        return {
            "key": self.key,
            "change_type": self.change_type,
            "severity": self.severity,
            "note": self.note,
            "hints": self.hints,
            "sensitive": self.sensitive,
        }


@dataclass
class AnnotateResult:
    """Result of annotating a diff."""

    annotations: List[Annotation] = field(default_factory=list)
    critical_count: int = 0
    warning_count: int = 0
    info_count: int = 0

    def to_summary(self) -> str:
        total = len(self.annotations)
        return (
            f"{total} annotation(s): "
            f"{self.critical_count} critical, "
            f"{self.warning_count} warning, "
            f"{self.info_count} info"
        )

    def to_dict(self) -> Dict:
        return {
            "critical_count": self.critical_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "annotations": [a.to_dict() for a in self.annotations],
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _determine_severity(change: EnvChange, sensitive: bool) -> str:
    """Return a severity level for the given change."""
    if sensitive:
        return "critical"
    if change.change_type == "removed":
        return "warning"
    return "info"


def _build_hints(change: EnvChange, sensitive: bool) -> List[str]:
    """Generate contextual hints for a change."""
    hints: List[str] = []

    if sensitive:
        hints.append("Value appears to be sensitive — avoid committing to VCS.")

    if change.change_type == "added":
        hints.append("New key introduced; ensure all environments are updated.")
    elif change.change_type == "removed":
        hints.append("Key was removed; verify no running service still depends on it.")
    elif change.change_type == "modified":
        if change.old_value == "" or change.new_value == "":
            hints.append("Value changed to/from empty string — may indicate misconfiguration.")
        else:
            hints.append("Value updated; confirm the change is intentional across all envs.")

    return hints


def _build_note(change: EnvChange, sensitive: bool) -> str:
    """Build a concise human-readable note."""
    if change.change_type == "added":
        preview = "[redacted]" if sensitive else repr(change.new_value)
        return f"Key '{change.key}' added with value {preview}."
    elif change.change_type == "removed":
        preview = "[redacted]" if sensitive else repr(change.old_value)
        return f"Key '{change.key}' removed (was {preview})."
    else:  # modified
        if sensitive:
            return f"Key '{change.key}' modified (sensitive — values redacted)."
        return (
            f"Key '{change.key}' changed from {repr(change.old_value)} "
            f"to {repr(change.new_value)}."
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def annotate_diff(diff: DiffResult) -> AnnotateResult:
    """Annotate every change in *diff* with severity, notes, and hints.

    Args:
        diff: A :class:`~envpatch.differ.DiffResult` produced by
              :func:`~envpatch.differ.diff_envs`.

    Returns:
        An :class:`AnnotateResult` containing one
        :class:`Annotation` per change.
    """
    result = AnnotateResult()

    for change in diff.changes:
        sensitive = is_sensitive(change.key)
        severity = _determine_severity(change, sensitive)
        note = _build_note(change, sensitive)
        hints = _build_hints(change, sensitive)

        annotation = Annotation(
            key=change.key,
            change_type=change.change_type,
            severity=severity,
            note=note,
            hints=hints,
            sensitive=sensitive,
        )
        result.annotations.append(annotation)

        if severity == "critical":
            result.critical_count += 1
        elif severity == "warning":
            result.warning_count += 1
        else:
            result.info_count += 1

    return result
