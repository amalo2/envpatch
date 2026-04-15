"""Snapshot support for capturing and restoring .env state."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from envpatch.parser import parse_env_file


@dataclass
class Snapshot:
    """Represents a point-in-time capture of an .env file."""

    source_path: str
    captured_at: str
    data: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "source_path": self.source_path,
            "captured_at": self.captured_at,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, raw: dict) -> "Snapshot":
        return cls(
            source_path=raw["source_path"],
            captured_at=raw["captured_at"],
            data=raw.get("data", {}),
        )

    def save(self, snapshot_path: str) -> None:
        """Persist snapshot to a JSON file."""
        Path(snapshot_path).write_text(
            json.dumps(self.to_dict(), indent=2), encoding="utf-8"
        )

    @classmethod
    def load(cls, snapshot_path: str) -> "Snapshot":
        """Load a snapshot from a JSON file."""
        raw = json.loads(Path(snapshot_path).read_text(encoding="utf-8"))
        return cls.from_dict(raw)


def capture_snapshot(env_path: str, snapshot_path: Optional[str] = None) -> Snapshot:
    """Capture current state of an .env file as a Snapshot."""
    data = parse_env_file(env_path)
    captured_at = datetime.now(timezone.utc).isoformat()
    snapshot = Snapshot(source_path=env_path, captured_at=captured_at, data=data)
    if snapshot_path:
        snapshot.save(snapshot_path)
    return snapshot


def restore_snapshot(snapshot: Snapshot, target_path: Optional[str] = None) -> str:
    """Serialize snapshot data back to .env format."""
    lines = [f"{k}={v}" for k, v in snapshot.data.items()]
    content = os.linesep.join(lines) + os.linesep if lines else ""
    out_path = target_path or snapshot.source_path
    Path(out_path).write_text(content, encoding="utf-8")
    return out_path
