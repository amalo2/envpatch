"""Key rotation: replace values for specified keys with new generated secrets."""
from __future__ import annotations

import secrets
import string
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envpatch.parser import parse_env_string
from envpatch.patcher import serialize_env

_ALPHABET = string.ascii_letters + string.digits


def _generate_secret(length: int = 32) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))


@dataclass
class RotateResult:
    env: Dict[str, str]
    rotated: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def rotated_count(self) -> int:
        return len(self.rotated)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def to_summary(self) -> str:
        return (
            f"Rotated {self.rotated_count} key(s), "
            f"skipped {self.skipped_count} key(s)."
        )


def rotate_keys(
    env_string: str,
    keys: List[str],
    length: int = 32,
    generator: Optional[callable] = None,
    skip_missing: bool = True,
) -> RotateResult:
    """Rotate (replace) values for the given keys with newly generated secrets.

    Args:
        env_string: Raw .env file contents.
        keys: List of key names whose values should be rotated.
        length: Length of the generated secret string.
        generator: Optional callable() -> str to produce a new value.
        skip_missing: If True, silently skip keys not present in env.
                      If False, raise KeyError for missing keys.

    Returns:
        RotateResult with updated env dict and lists of rotated/skipped keys.
    """
    gen = generator or (lambda: _generate_secret(length))
    env = parse_env_string(env_string)
    rotated: List[str] = []
    skipped: List[str] = []

    for key in keys:
        if key not in env:
            if skip_missing:
                skipped.append(key)
            else:
                raise KeyError(f"Key '{key}' not found in env.")
            continue
        env[key] = gen()
        rotated.append(key)

    return RotateResult(env=env, rotated=rotated, skipped=skipped)
