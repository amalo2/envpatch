"""Unpack a .env archive (zip) back into individual .env files."""
from __future__ import annotations

import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class UnpackResult:
    extracted: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    destination: str = ""

    @property
    def extracted_count(self) -> int:
        return len(self.extracted)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def to_summary(self) -> str:
        lines = [
            f"Destination : {self.destination}",
            f"Extracted   : {self.extracted_count}",
            f"Skipped     : {self.skipped_count}",
        ]
        if self.extracted:
            lines.append("Files:")
            for name in self.extracted:
                lines.append(f"  + {name}")
        if self.skipped:
            lines.append("Skipped:")
            for name in self.skipped:
                lines.append(f"  ~ {name}")
        return "\n".join(lines)


def unpack_env(
    archive_path: str,
    dest_dir: str = ".",
    overwrite: bool = False,
    pattern: Optional[str] = None,
) -> UnpackResult:
    """Extract .env files from a zip archive into *dest_dir*.

    Args:
        archive_path: Path to the zip archive produced by ``archive_envs``.
        dest_dir:     Directory to extract files into (created if absent).
        overwrite:    When *False* (default) existing files are skipped.
        pattern:      Optional glob-style substring filter on member names.

    Returns:
        :class:`UnpackResult` describing what was extracted or skipped.
    """
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)

    result = UnpackResult(destination=str(dest.resolve()))

    with zipfile.ZipFile(archive_path, "r") as zf:
        members = zf.namelist()
        for member in members:
            if pattern and pattern not in member:
                continue
            target = dest / member
            if target.exists() and not overwrite:
                result.skipped.append(member)
                continue
            zf.extract(member, path=dest)
            result.extracted.append(member)

    return result
