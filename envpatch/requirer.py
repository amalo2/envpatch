"""Check that required keys are present in an env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envpatch.parser import parse_env_string


@dataclass
class RequireResult:
    required: List[str]
    present: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    @property
    def is_satisfied(self) -> bool:
        return len(self.missing) == 0

    @property
    def missing_count(self) -> int:
        return len(self.missing)

    @property
    def present_count(self) -> int:
        return len(self.present)

    def to_summary(self) -> str:
        lines = [
            f"Required : {len(self.required)}",
            f"Present  : {self.present_count}",
            f"Missing  : {self.missing_count}",
        ]
        if self.missing:
            lines.append("Missing keys:")
            for key in self.missing:
                lines.append(f"  - {key}")
        return "\n".join(lines)


def require_keys(env_string: str, required: List[str]) -> RequireResult:
    """Check that all *required* keys exist in *env_string*."""
    env = parse_env_string(env_string)
    present: List[str] = []
    missing: List[str] = []

    for key in required:
        if key in env:
            present.append(key)
        else:
            missing.append(key)

    return RequireResult(
        required=list(required),
        present=present,
        missing=missing,
        env=env,
    )
