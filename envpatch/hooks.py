"""Optional audit hook integration for CLI operations."""
from __future__ import annotations

import os
from typing import Optional

from envpatch.auditor import AuditEntry, make_entry, append_to_log
from envpatch.differ import DiffResult
from envpatch.merger import MergeResult

ENV_AUDIT_LOG = "ENVPATCH_AUDIT_LOG"


def _get_log_path() -> Optional[str]:
    """Return audit log path from environment variable, or None if unset."""
    return os.environ.get(ENV_AUDIT_LOG)


def audit_diff(
    diff: DiffResult,
    source: Optional[str] = None,
    target: Optional[str] = None,
) -> Optional[AuditEntry]:
    """Record a diff operation to the audit log if configured."""
    log_path = _get_log_path()
    if not log_path:
        return None
    entry = make_entry(
        operation="diff",
        source=source,
        target=target,
        keys_added=list(diff.added),
        keys_removed=list(diff.removed),
        keys_modified=[c.key for c in diff.modified],
    )
    append_to_log(entry, log_path)
    return entry


def audit_merge(
    result: MergeResult,
    source: Optional[str] = None,
    target: Optional[str] = None,
) -> Optional[AuditEntry]:
    """Record a merge operation to the audit log if configured."""
    log_path = _get_log_path()
    if not log_path:
        return None
    entry = make_entry(
        operation="merge",
        source=source,
        target=target,
        keys_added=list(result.applied),
        keys_skipped=list(result.skipped),
    )
    append_to_log(entry, log_path)
    return entry


def audit_snapshot(
    keys: list,
    source: Optional[str] = None,
    notes: Optional[str] = None,
) -> Optional[AuditEntry]:
    """Record a snapshot operation to the audit log if configured."""
    log_path = _get_log_path()
    if not log_path:
        return None
    entry = make_entry(
        operation="snapshot",
        source=source,
        keys_added=list(keys),
        notes=notes,
    )
    append_to_log(entry, log_path)
    return entry
