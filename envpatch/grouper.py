from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envpatch.parser import parse_env_string


@dataclass
class GroupResult:
    groups: Dict[str, Dict[str, str]] = field(default_factory=dict)
    ungrouped: Dict[str, str] = field(default_factory=dict)
    key_count: int = 0

    def group_count(self) -> int:
        return len(self.groups)

    def to_summary(self) -> str:
        lines = [f"Groups: {self.group_count()}, Keys: {self.key_count}"]
        for name, keys in self.groups.items():
            lines.append(f"  [{name}] {len(keys)} key(s)")
        if self.ungrouped:
            lines.append(f"  [ungrouped] {len(self.ungrouped)} key(s)")
        return "\n".join(lines)


def group_env(env_string: str, delimiter: str = "_") -> GroupResult:
    """
    Group env keys by their prefix (the part before the first delimiter).
    Keys with no delimiter are placed in 'ungrouped'.
    """
    parsed = parse_env_string(env_string)
    groups: Dict[str, Dict[str, str]] = {}
    ungrouped: Dict[str, str] = {}

    for key, value in parsed.items():
        if delimiter in key:
            prefix = key.split(delimiter, 1)[0]
            groups.setdefault(prefix, {})
            groups[prefix][key] = value
        else:
            ungrouped[key] = value

    return GroupResult(
        groups=groups,
        ungrouped=ungrouped,
        key_count=len(parsed),
    )


def filter_group(result: GroupResult, prefix: str) -> Optional[Dict[str, str]]:
    """Return keys for a specific group prefix, or None if not found."""
    return result.groups.get(prefix)
