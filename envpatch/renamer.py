"""Rename keys across .env content with optional dry-run support."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envpatch.parser import parse_env_string


@dataclass
class RenameResult:
    renamed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    output: str = ""

    @property
    def renamed_count(self) -> int:
        return len(self.renamed)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def to_summary(self) -> str:
        lines = [f"Renamed: {self.renamed_count}  Skipped: {self.skipped_count}"]
        for key in self.renamed:
            lines.append(f"  ~ {key}")
        for key in self.skipped:
            lines.append(f"  - {key} (not found)")
        return "\n".join(lines)


def rename_keys(
    content: str,
    renames: Dict[str, str],
    overwrite_existing: bool = False,
) -> RenameResult:
    """Rename keys in env content according to the renames mapping.

    Args:
        content: Raw .env file content.
        renames: Mapping of {old_key: new_key}.
        overwrite_existing: If True, overwrite new_key even if it already exists.

    Returns:
        RenameResult with details of what was renamed or skipped.
    """
    existing = parse_env_string(content)
    result = RenameResult()
    output_lines: List[str] = []

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            output_lines.append(line)
            continue

        if "=" not in stripped:
            output_lines.append(line)
            continue

        key, _, rest = stripped.partition("=")
        key = key.strip()

        if key in renames:
            new_key = renames[key]
            if new_key in existing and not overwrite_existing:
                result.skipped.append(key)
                output_lines.append(line)
            else:
                result.renamed.append(key)
                output_lines.append(f"{new_key}={rest}")
        else:
            output_lines.append(line)

    for old_key in renames:
        if old_key not in existing and old_key not in result.renamed:
            result.skipped.append(old_key)

    result.output = "\n".join(output_lines)
    if content.endswith("\n") and not result.output.endswith("\n"):
        result.output += "\n"

    return result
