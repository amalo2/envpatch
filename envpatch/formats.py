"""Format registry for envpatch output formats."""
from __future__ import annotations

from typing import Callable

from envpatch.differ import DiffResult
from envpatch.exporter import diff_to_dotenv_patch, diff_to_json


def _diff_to_text(diff: DiffResult) -> str:
    """Render diff as human-readable text lines."""
    lines: list[str] = []
    for key, change in sorted(diff.changes.items()):
        lines.append(str(change))
    return "\n".join(lines) + ("\n" if lines else "")


# Registry maps format name -> callable(DiffResult) -> str
_DIFF_FORMATS: dict[str, Callable[[DiffResult], str]] = {
    "text": _diff_to_text,
    "json": diff_to_json,
    "patch": diff_to_dotenv_patch,
}

SUPPORTED_FORMATS: list[str] = list(_DIFF_FORMATS.keys())


def format_diff(diff: DiffResult, fmt: str = "text") -> str:
    """Format a DiffResult using the specified format name.

    Args:
        diff: The diff result to format.
        fmt: One of 'text', 'json', or 'patch'.

    Returns:
        Formatted string representation.

    Raises:
        ValueError: If the format is not supported.
    """
    if fmt not in _DIFF_FORMATS:
        raise ValueError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )
    return _DIFF_FORMATS[fmt](diff)


def register_format(name: str, formatter: Callable[[DiffResult], str]) -> None:
    """Register a custom diff formatter.

    Args:
        name: Unique format identifier.
        formatter: Callable that accepts a DiffResult and returns a string.
    """
    if not callable(formatter):
        raise TypeError("formatter must be callable")
    _DIFF_FORMATS[name] = formatter
    if name not in SUPPORTED_FORMATS:
        SUPPORTED_FORMATS.append(name)
