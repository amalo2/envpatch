"""Pruner: remove keys with empty, null, or placeholder values from an env mapping."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envpatch.parser import parse_env_string
from envpatch.patcher import serialize_env

# Values considered empty / placeholder
_PLACEHOLDER_PATTERNS: List[re.Pattern] = [
    re.compile(r"^$"),                        # empty string
    re.compile(r"^null$", re.IGNORECASE),
    re.compile(r"^none$", re.IGNORECASE),
    re.compile(r"^(todo|fixme|changeme|placeholder|your[_-]?.*here)$", re.IGNORECASE),
    re.compile(r"^<[^>]+>$"),                 # <VALUE>, <YOUR_SECRET>, etc.
    re.compile(r"^\[.*\]$"),                  # [value], [FILL ME]
]


def _is_prunable(value: str) -> bool:
    """Return True when *value* matches any placeholder pattern."""
    return any(p.match(value) for p in _PLACEHOLDER_PATTERNS)


@dataclass
class PruneResult:
    env: Dict[str, str]
    pruned: List[str] = field(default_factory=list)
    kept: List[str] = field(default_factory=list)

    @property
    def pruned_count(self) -> int:
        return len(self.pruned)

    @property
    def kept_count(self) -> int:
        return len(self.kept)

    def to_summary(self) -> str:
        return (
            f"Pruned {self.pruned_count} key(s), "
            f"kept {self.kept_count} key(s)."
        )


def prune_env(
    source: str,
    *,
    extra_patterns: Optional[List[str]] = None,
    keys: Optional[List[str]] = None,
) -> PruneResult:
    """Parse *source* and remove keys whose values are empty or placeholder-like.

    Args:
        source: Raw .env file content.
        extra_patterns: Additional regex patterns to treat as prunable.
        keys: If provided, only consider these specific keys for pruning.

    Returns:
        A :class:`PruneResult` with the cleaned env dict and accounting lists.
    """
    compiled_extras: List[re.Pattern] = [
        re.compile(p, re.IGNORECASE) for p in (extra_patterns or [])
    ]

    parsed = parse_env_string(source)
    pruned: List[str] = []
    kept: List[str] = []
    result: Dict[str, str] = {}

    for k, v in parsed.items():
        candidate = keys is None or k in keys
        if candidate and (_is_prunable(v) or any(p.match(v) for p in compiled_extras)):
            pruned.append(k)
        else:
            kept.append(k)
            result[k] = v

    return PruneResult(env=result, pruned=pruned, kept=kept)
