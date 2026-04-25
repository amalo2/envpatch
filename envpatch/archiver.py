"""Archive .env files into a timestamped bundle with optional metadata."""

from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ArchiveResult:
    archive_path: str
    files_archived: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    created_at: str = ""

    @property
    def archived_count(self) -> int:
        return len(self.files_archived)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def to_summary(self) -> str:
        lines = [
            f"Archive : {self.archive_path}",
            f"Archived: {self.archived_count} file(s)",
            f"Skipped : {self.skipped_count} file(s)",
            f"Created : {self.created_at}",
        ]
        if self.files_archived:
            lines.append("Files   : " + ", ".join(self.files_archived))
        return "\n".join(lines)


def archive_envs(
    paths: List[str],
    output_dir: str = ".",
    label: Optional[str] = None,
    include_metadata: bool = True,
) -> ArchiveResult:
    """Bundle one or more .env files into a timestamped zip archive."""
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%dT%H%M%SZ")
    stem = f"envpatch-{label}-{timestamp}" if label else f"envpatch-{timestamp}"
    archive_path = str(Path(output_dir) / f"{stem}.zip")

    result = ArchiveResult(archive_path=archive_path, created_at=now.isoformat())

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for raw_path in paths:
            p = Path(raw_path)
            if not p.exists() or not p.is_file():
                result.skipped.append(raw_path)
                continue
            zf.write(p, arcname=p.name)
            result.files_archived.append(p.name)

        if include_metadata:
            meta: Dict = {
                "created_at": now.isoformat(),
                "label": label,
                "files": result.files_archived,
                "skipped": result.skipped,
            }
            zf.writestr("_meta.json", json.dumps(meta, indent=2))

    return result
