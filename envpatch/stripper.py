"""Strip keys from .env content by pattern or explicit list."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Sequence
import re

from envpatch.parser import parse_env_string


@dataclass
class StripResult:
    output: str
    stripped: list[str] = field(default_factory=list)
    kept: list[str] = field(default_factory=list)

    @property
    def stripped_count(self) -> int:
        return len(self.stripped)

    @property
    def kept_count(self) -> int:
        return len(self.kept)

    def to_summary(self) -> str:
        return (
            f"Stripped {self.stripped_count} key(s), "
            f"kept {self.kept_count} key(s)."
        )


def strip_keys(
    env_string: str,
    keys: Sequence[str] | None = None,
    patterns: Sequence[str] | None = None,
) -> StripResult:
    """Remove keys from env_string by explicit name or regex pattern."""
    compiled = [re.compile(p) for p in (patterns or [])]
    explicit = set(keys or [])

    parsed = parse_env_string(env_string)
    to_strip: set[str] = set()

    for key in parsed:
        if key in explicit:
            to_strip.add(key)
            continue
        for pat in compiled:
            if pat.search(key):
                to_strip.add(key)
                break

    output_lines: list[str] = []
    for line in env_string.splitlines():
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("#"):
            output_lines.append(line)
            continue
        if "=" not in stripped_line:
            output_lines.append(line)
            continue
        k = stripped_line.split("=", 1)[0].strip()
        if k not in to_strip:
            output_lines.append(line)

    kept = [k for k in parsed if k not in to_strip]
    return StripResult(
        output="\n".join(output_lines),
        stripped=sorted(to_strip),
        kept=kept,
    )
