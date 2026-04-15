"""Compare two snapshots and produce a structured comparison result."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envpatch.snapshot import Snapshot
from envpatch.differ import diff_envs, DiffResult


@dataclass
class CompareResult:
    """Result of comparing two snapshots."""

    source_path: Optional[str]
    target_path: Optional[str]
    source_timestamp: Optional[str]
    target_timestamp: Optional[str]
    diff: DiffResult

    @property
    def added_count(self) -> int:
        return len(self.diff.added)

    @property
    def removed_count(self) -> int:
        return len(self.diff.removed)

    @property
    def modified_count(self) -> int:
        return len(self.diff.modified)

    @property
    def has_changes(self) -> bool:
        return self.added_count > 0 or self.removed_count > 0 or self.modified_count > 0

    def to_summary(self) -> str:
        lines = [
            f"Source:   {self.source_path or 'unknown'} (captured: {self.source_timestamp or 'unknown'})",
            f"Target:   {self.target_path or 'unknown'} (captured: {self.target_timestamp or 'unknown'})",
            f"Added:    {self.added_count}",
            f"Removed:  {self.removed_count}",
            f"Modified: {self.modified_count}",
        ]
        if not self.has_changes:
            lines.append("No differences found.")
        return "\n".join(lines)


def compare_snapshots(source: Snapshot, target: Snapshot) -> CompareResult:
    """Diff two snapshots and return a CompareResult."""
    diff = diff_envs(source.data, target.data)
    return CompareResult(
        source_path=source.source_path,
        target_path=target.source_path,
        source_timestamp=source.captured_at,
        target_timestamp=target.captured_at,
        diff=diff,
    )


def compare_snapshot_files(source_path: str, target_path: str) -> CompareResult:
    """Load two snapshot files from disk and compare them."""
    from envpatch.snapshot import Snapshot

    source = Snapshot.load(source_path)
    target = Snapshot.load(target_path)
    return compare_snapshots(source, target)
