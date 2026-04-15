"""Export env diffs and merge results to various formats."""
from __future__ import annotations

import json
from typing import Any

from envpatch.differ import DiffResult
from envpatch.merger import MergeResult


def diff_to_dict(diff: DiffResult) -> dict[str, Any]:
    """Convert a DiffResult to a plain dictionary."""
    return {
        "added": {k: v.new_value for k, v in diff.changes.items() if v.change_type == "added"},
        "removed": {k: v.old_value for k, v in diff.changes.items() if v.change_type == "removed"},
        "modified": {
            k: {"old": v.old_value, "new": v.new_value}
            for k, v in diff.changes.items()
            if v.change_type == "modified"
        },
    }


def diff_to_json(diff: DiffResult, indent: int = 2) -> str:
    """Serialize a DiffResult to a JSON string."""
    return json.dumps(diff_to_dict(diff), indent=indent)


def merge_result_to_dict(result: MergeResult) -> dict[str, Any]:
    """Convert a MergeResult to a plain dictionary."""
    return {
        "applied": result.applied,
        "skipped": result.skipped,
        "applied_count": result.applied_count,
        "skipped_count": result.skipped_count,
    }


def merge_result_to_json(result: MergeResult, indent: int = 2) -> str:
    """Serialize a MergeResult to a JSON string."""
    return json.dumps(merge_result_to_dict(result), indent=indent)


def diff_to_dotenv_patch(diff: DiffResult) -> str:
    """Render a DiffResult as a .env-style patch file (added/modified keys only)."""
    lines: list[str] = []
    for key, change in sorted(diff.changes.items()):
        if change.change_type in ("added", "modified"):
            value = change.new_value or ""
            if " " in value or "#" in value:
                value = f'"{value}"'
            lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")
