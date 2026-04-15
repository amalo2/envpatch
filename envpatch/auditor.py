"""Audit log for tracking env patch operations."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


@dataclass
class AuditEntry:
    operation: str  # 'diff', 'apply', 'merge', 'snapshot'
    timestamp: str
    source: Optional[str] = None
    target: Optional[str] = None
    keys_added: List[str] = field(default_factory=list)
    keys_removed: List[str] = field(default_factory=list)
    keys_modified: List[str] = field(default_factory=list)
    keys_skipped: List[str] = field(default_factory=list)
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "operation": self.operation,
            "timestamp": self.timestamp,
            "source": self.source,
            "target": self.target,
            "keys_added": self.keys_added,
            "keys_removed": self.keys_removed,
            "keys_modified": self.keys_modified,
            "keys_skipped": self.keys_skipped,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AuditEntry":
        return cls(
            operation=data["operation"],
            timestamp=data["timestamp"],
            source=data.get("source"),
            target=data.get("target"),
            keys_added=data.get("keys_added", []),
            keys_removed=data.get("keys_removed", []),
            keys_modified=data.get("keys_modified", []),
            keys_skipped=data.get("keys_skipped", []),
            notes=data.get("notes"),
        )


def make_entry(
    operation: str,
    source: Optional[str] = None,
    target: Optional[str] = None,
    keys_added: Optional[List[str]] = None,
    keys_removed: Optional[List[str]] = None,
    keys_modified: Optional[List[str]] = None,
    keys_skipped: Optional[List[str]] = None,
    notes: Optional[str] = None,
) -> AuditEntry:
    return AuditEntry(
        operation=operation,
        timestamp=datetime.now(timezone.utc).isoformat(),
        source=source,
        target=target,
        keys_added=keys_added or [],
        keys_removed=keys_removed or [],
        keys_modified=keys_modified or [],
        keys_skipped=keys_skipped or [],
        notes=notes,
    )


def append_to_log(entry: AuditEntry, log_path: str) -> None:
    path = Path(log_path)
    entries: List[dict] = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            entries = json.load(f)
    entries.append(entry.to_dict())
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def load_log(log_path: str) -> List[AuditEntry]:
    path = Path(log_path)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [AuditEntry.from_dict(d) for d in raw]
