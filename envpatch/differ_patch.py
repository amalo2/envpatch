"""Generate a patch .env string from a DiffResult, applying only selected change types."""

from dataclasses import dataclass, field
from typing import Optional

from envpatch.differ import DiffResult, EnvChange


@dataclass
class PatchGenResult:
    patch_env: str
    included_count: int = 0
    skipped_count: int = 0
    change_types: list = field(default_factory=list)

    def to_summary(self) -> str:
        return (
            f"Patch generated: {self.included_count} included, "
            f"{self.skipped_count} skipped "
            f"(types: {', '.join(self.change_types) or 'none'})"
        )


def generate_patch(
    diff: DiffResult,
    include_added: bool = True,
    include_modified: bool = True,
    include_removed: bool = False,
    prefix_comments: bool = True,
) -> PatchGenResult:
    """Generate a patch .env string from a DiffResult.

    Args:
        diff: The DiffResult to generate a patch from.
        include_added: Include newly added keys.
        include_modified: Include modified keys (uses new value).
        include_removed: Include removed keys as commented-out entries.
        prefix_comments: Add a comment above each entry describing the change.

    Returns:
        PatchGenResult with the patch content and metadata.
    """
    lines: list[str] = []
    included = 0
    skipped = 0
    types_used: set[str] = set()

    def _emit(change: EnvChange, label: str, value: Optional[str], comment: bool) -> None:
        nonlocal included
        if comment and prefix_comments:
            lines.append(f"# {label}: {change.key}")
        if value is not None:
            lines.append(f"{change.key}={value}")
        else:
            lines.append(f"# {change.key}=  (removed)")
        lines.append("")
        included += 1

    all_changes: list[EnvChange] = list(diff.changes)

    for change in all_changes:
        ct = change.change_type
        if ct == "added" and include_added:
            _emit(change, "ADDED", change.new_value, True)
            types_used.add("added")
        elif ct == "modified" and include_modified:
            _emit(change, "MODIFIED", change.new_value, True)
            types_used.add("modified")
        elif ct == "removed" and include_removed:
            _emit(change, "REMOVED", None, True)
            types_used.add("removed")
        else:
            skipped += 1

    patch_env = "\n".join(lines).rstrip("\n")

    return PatchGenResult(
        patch_env=patch_env,
        included_count=included,
        skipped_count=skipped,
        change_types=sorted(types_used),
    )
