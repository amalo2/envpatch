from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AliasResult:
    env: Dict[str, str]
    aliased: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def aliased_count(self) -> int:
        return len(self.aliased)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def to_summary(self) -> str:
        return (
            f"Aliased: {self.aliased_count}, Skipped: {self.skipped_count}"
        )


def alias_keys(
    env: Dict[str, str],
    aliases: Dict[str, str],
    overwrite: bool = False,
) -> AliasResult:
    """Copy values from existing keys to new alias keys.

    Args:
        env: Source environment dict.
        aliases: Mapping of existing_key -> alias_key.
        overwrite: If True, overwrite alias key if it already exists.

    Returns:
        AliasResult with updated env and tracking lists.
    """
    result_env = dict(env)
    aliased: List[str] = []
    skipped: List[str] = []

    for source_key, alias_key in aliases.items():
        if source_key not in env:
            skipped.append(source_key)
            continue
        if alias_key in result_env and not overwrite:
            skipped.append(source_key)
            continue
        result_env[alias_key] = env[source_key]
        aliased.append(source_key)

    return AliasResult(env=result_env, aliased=aliased, skipped=skipped)
