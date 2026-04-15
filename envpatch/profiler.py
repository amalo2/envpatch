"""Profile .env files to detect patterns, stats, and anomalies."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envpatch.redactor import is_sensitive


@dataclass
class ProfileResult:
    total_keys: int = 0
    sensitive_keys: List[str] = field(default_factory=list)
    blank_value_keys: List[str] = field(default_factory=list)
    duplicate_values: Dict[str, List[str]] = field(default_factory=dict)
    longest_key: str = ""
    longest_value_key: str = ""

    @property
    def sensitive_count(self) -> int:
        return len(self.sensitive_keys)

    @property
    def blank_count(self) -> int:
        return len(self.blank_value_keys)

    def to_summary(self) -> str:
        lines = [
            f"Total keys      : {self.total_keys}",
            f"Sensitive keys  : {self.sensitive_count}",
            f"Blank values    : {self.blank_count}",
            f"Duplicate values: {len(self.duplicate_values)}",
        ]
        if self.longest_key:
            lines.append(f"Longest key     : {self.longest_key}")
        if self.longest_value_key:
            lines.append(f"Longest value   : {self.longest_value_key}")
        return "\n".join(lines)


def profile_env(env: Dict[str, str]) -> ProfileResult:
    """Analyse an env dict and return a ProfileResult."""
    result = ProfileResult(total_keys=len(env))

    value_map: Dict[str, List[str]] = {}
    longest_key = ""
    longest_value_key = ""

    for key, value in env.items():
        if is_sensitive(key):
            result.sensitive_keys.append(key)

        if value == "":
            result.blank_value_keys.append(key)

        value_map.setdefault(value, []).append(key)

        if len(key) > len(longest_key):
            longest_key = key

        if len(value) > len(env.get(longest_value_key, "")):
            longest_value_key = key

    result.longest_key = longest_key
    result.longest_value_key = longest_value_key
    result.duplicate_values = {
        v: keys for v, keys in value_map.items() if len(keys) > 1 and v != ""
    }

    return result
