"""Inject environment variables from a .env file into the current process environment."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envpatch.parser import parse_env_string


@dataclass
class InjectResult:
    injected: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    @property
    def injected_count(self) -> int:
        return len(self.injected)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def to_summary(self) -> str:
        return (
            f"Injected {self.injected_count} key(s), "
            f"skipped {self.skipped_count} key(s) (already set)."
        )


def inject_env(
    env_string: str,
    *,
    overwrite: bool = False,
    prefix: Optional[str] = None,
    target: Optional[Dict[str, str]] = None,
) -> InjectResult:
    """Inject parsed .env variables into *target* (defaults to ``os.environ``).

    Args:
        env_string: Raw .env file content.
        overwrite: When True, existing environment variables are overwritten.
        prefix: Optional prefix to prepend to every key before injection.
        target: Mapping to inject into; defaults to ``os.environ``.

    Returns:
        An :class:`InjectResult` describing what was injected or skipped.
    """
    if target is None:
        target = os.environ  # type: ignore[assignment]

    parsed = parse_env_string(env_string)
    result = InjectResult(env=dict(target))

    for key, value in parsed.items():
        dest_key = f"{prefix}{key}" if prefix else key
        if dest_key in target and not overwrite:
            result.skipped.append(dest_key)
        else:
            target[dest_key] = value
            result.env[dest_key] = value
            result.injected.append(dest_key)

    return result
