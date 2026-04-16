from dataclasses import dataclass, field
from typing import Dict, List

from envpatch.parser import parse_env_string


@dataclass
class DuplicateResult:
    duplicates: Dict[str, List[int]] = field(default_factory=dict)
    env: Dict[str, str] = field(default_factory=dict)

    @property
    def duplicate_count(self) -> int:
        return len(self.duplicates)

    @property
    def has_duplicates(self) -> bool:
        return bool(self.duplicates)

    def to_summary(self) -> str:
        if not self.has_duplicates:
            return "No duplicate keys found."
        lines = [f"Found {self.duplicate_count} duplicate key(s):"]
        for key, linenos in self.duplicates.items():
            lines.append(f"  {key}: lines {', '.join(str(n) for n in linenos)}")
        return "\n".join(lines)


def find_duplicates(env_string: str) -> DuplicateResult:
    """Scan env string for duplicate keys, tracking line numbers."""
    seen: Dict[str, List[int]] = {}
    for lineno, raw_line in enumerate(env_string.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        if not key:
            continue
        seen.setdefault(key, []).append(lineno)

    duplicates = {k: v for k, v in seen.items() if len(v) > 1}
    env = parse_env_string(env_string)
    return DuplicateResult(duplicates=duplicates, env=env)
