from dataclasses import dataclass, field
from typing import Dict, List
from envpatch.parser import parse_env_string


@dataclass
class FreezeResult:
    frozen: Dict[str, str] = field(default_factory=dict)
    frozen_keys: List[str] = field(default_factory=list)
    skipped_keys: List[str] = field(default_factory=list)

    @property
    def frozen_count(self) -> int:
        return len(self.frozen_keys)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped_keys)

    def to_summary(self) -> str:
        return (
            f"Frozen: {self.frozen_count} key(s), "
            f"Skipped: {self.skipped_count} key(s)"
        )


def freeze_env(
    env_string: str,
    keys: List[str] = None,
    marker: str = "# frozen",
) -> FreezeResult:
    """Mark specific keys (or all) as frozen by appending a marker comment."""
    result = FreezeResult()
    parsed = parse_env_string(env_string)
    lines = env_string.splitlines()
    output_lines = []

    frozen_set = set(keys) if keys else set(parsed.keys())

    annotated = set()
    for line in lines:
        stripped = line.strip()
        if "=" in stripped and not stripped.startswith("#"):
            key = stripped.split("=", 1)[0].strip()
            if key in frozen_set and key not in annotated:
                if not line.rstrip().endswith(marker):
                    line = line.rstrip() + f"  {marker}"
                result.frozen_keys.append(key)
                result.frozen[key] = parsed.get(key, "")
                annotated.add(key)
            else:
                if key not in frozen_set:
                    result.skipped_keys.append(key)
        output_lines.append(line)

    result.frozen["__output__"] = "\n".join(output_lines)
    return result


def is_frozen(line: str, marker: str = "# frozen") -> bool:
    return marker in line
