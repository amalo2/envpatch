"""Redactor module for masking sensitive values in .env output."""

from __future__ import annotations

import re
from typing import Dict, List, Optional

# Default patterns considered sensitive
DEFAULT_SENSITIVE_PATTERNS: List[str] = [
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*PASSWD.*",
    r".*TOKEN.*",
    r".*API_KEY.*",
    r".*PRIVATE.*",
    r".*CREDENTIAL.*",
]

REDACTED_PLACEHOLDER = "***REDACTED***"


def _compile_patterns(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def is_sensitive(key: str, patterns: Optional[List[str]] = None) -> bool:
    """Return True if the key matches any sensitive pattern."""
    compiled = _compile_patterns(patterns or DEFAULT_SENSITIVE_PATTERNS)
    return any(pat.fullmatch(key) for pat in compiled)


def redact_value(key: str, value: str, patterns: Optional[List[str]] = None) -> str:
    """Return REDACTED_PLACEHOLDER if the key is sensitive, otherwise return value."""
    if is_sensitive(key, patterns):
        return REDACTED_PLACEHOLDER
    return value


def redact_env(
    env: Dict[str, str],
    patterns: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Return a copy of env dict with sensitive values replaced."""
    return {
        key: redact_value(key, value, patterns)
        for key, value in env.items()
    }


def redact_diff_changes(
    changes: List,
    patterns: Optional[List[str]] = None,
) -> List:
    """Return a new list of EnvChange objects with sensitive values masked."""
    from envpatch.differ import EnvChange

    redacted: List[EnvChange] = []
    for change in changes:
        old = (
            redact_value(change.key, change.old_value, patterns)
            if change.old_value is not None
            else None
        )
        new = (
            redact_value(change.key, change.new_value, patterns)
            if change.new_value is not None
            else None
        )
        redacted.append(EnvChange(key=change.key, old_value=old, new_value=new))
    return redacted
