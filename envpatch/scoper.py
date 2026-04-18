from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envpatch.parser import parse_env_string


@dataclass
class ScopeResult:
    scope: str
    env: Dict[str, str]
    included: List[str] = field(default_factory=list)
    excluded: List[str] = field(default_factory=list)

    @property
    def included_count(self) -> int:
        return len(self.included)

    @property
    def excluded_count(self) -> int:
        return len(self.excluded)

    def to_summary(self) -> str:
        return (
            f"Scope : {self.scope}\n"
            f"Included : {self.included_count}\n"
            f"Excluded : {self.excluded_count}"
        )


def scope_env(
    source: str,
    scope: str,
    prefixes: Optional[List[str]] = None,
    strip_prefix: bool = False,
) -> ScopeResult:
    """Filter env keys to those matching a named scope (prefix list)."""
    parsed = parse_env_string(source)
    scope_prefixes = prefixes if prefixes else [scope.upper() + "_"]

    included: Dict[str, str] = {}
    excluded: Dict[str, str] = {}
    included_keys: List[str] = []
    excluded_keys: List[str] = []

    for key, value in parsed.items():
        matched = any(key.startswith(p) for p in scope_prefixes)
        if matched:
            out_key = key
            if strip_prefix:
                for p in scope_prefixes:
                    if key.startswith(p):
                        out_key = key[len(p):]
                        break
            included[out_key] = value
            included_keys.append(key)
        else:
            excluded[key] = value
            excluded_keys.append(key)

    return ScopeResult(
        scope=scope,
        env=included,
        included=included_keys,
        excluded=excluded_keys,
    )
