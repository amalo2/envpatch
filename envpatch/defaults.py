"""Fill missing keys in a target env from a defaults env."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envpatch.parser import parse_env_string


@dataclass
class DefaultsResult:
    filled: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    applied: List[str] = field(default_factory=list)

    @property
    def filled_count(self) -> int:
        return len(self.applied)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def to_summary(self) -> str:
        return (
            f"Defaults applied: {self.filled_count} filled, "
            f"{self.skipped_count} already present"
        )


def apply_defaults(
    target: str,
    defaults: str,
    overwrite: bool = False,
) -> DefaultsResult:
    """Apply default values from *defaults* env string into *target* env string.

    Keys already present in *target* are skipped unless *overwrite* is True.
    Returns a DefaultsResult with the merged env dict and change lists.
    """
    target_env = parse_env_string(target)
    defaults_env = parse_env_string(defaults)

    result = DefaultsResult(filled=dict(target_env))

    for key, value in defaults_env.items():
        if key in target_env and not overwrite:
            result.skipped.append(key)
        else:
            if key not in target_env:
                result.applied.append(key)
            elif overwrite and target_env[key] != value:
                result.applied.append(key)
            else:
                result.skipped.append(key)
                continue
            result.filled[key] = value

    return result
