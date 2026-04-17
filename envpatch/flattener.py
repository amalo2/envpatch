from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class FlattenResult:
    flattened: Dict[str, str] = field(default_factory=dict)
    promoted: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    fmt: str = "flat"

    @property
    def promoted_count(self) -> int:
        return len(self.promoted)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def to_summary(self) -> str:
        return (
            f"Flattened: {len(self.flattened)} keys "
            f"({self.promoted_count} promoted, {self.skipped_count} skipped)"
        )


def flatten_env(
    env: Dict[str, str],
    prefix: str = "",
    separator: str = "__",
    uppercase: bool = True,
) -> FlattenResult:
    """Flatten nested key segments (split by separator) and optionally apply prefix filter."""
    result = FlattenResult()

    for key, value in env.items():
        normalised = key.upper() if uppercase else key

        if prefix:
            expected = prefix.upper() if uppercase else prefix
            if not normalised.startswith(expected + separator):
                result.skipped.append(key)
                continue
            short_key = normalised[len(expected) + len(separator):]
        else:
            short_key = normalised

        if not short_key:
            result.skipped.append(key)
            continue

        result.flattened[short_key] = value
        result.promoted.append(key)

    return result
