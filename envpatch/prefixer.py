from dataclasses import dataclass, field
from typing import Dict, List
from envpatch.parser import parse_env_string
from envpatch.patcher import serialize_env


@dataclass
class PrefixResult:
    env: Dict[str, str]
    prefixed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def prefixed_count(self) -> int:
        return len(self.prefixed)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def to_summary(self) -> str:
        return (
            f"Prefixed: {self.prefixed_count} key(s), "
            f"skipped: {self.skipped_count} already-prefixed key(s)."
        )


def prefix_env(
    source: str,
    prefix: str,
    skip_existing: bool = True,
    strip: bool = False,
) -> PrefixResult:
    """Add *prefix* to every key in *source*.

    Args:
        source: Raw .env string.
        prefix: Prefix string to prepend (e.g. "APP_").
        skip_existing: When True, keys already starting with *prefix* are left
            unchanged and recorded in ``skipped``.
        strip: When True, remove *prefix* from keys instead of adding it.
    """
    parsed = parse_env_string(source)
    out: Dict[str, str] = {}
    prefixed: List[str] = []
    skipped: List[str] = []

    for key, value in parsed.items():
        if strip:
            if key.startswith(prefix):
                new_key = key[len(prefix):]
                out[new_key] = value
                prefixed.append(key)
            else:
                out[key] = value
                skipped.append(key)
        else:
            if skip_existing and key.startswith(prefix):
                out[key] = value
                skipped.append(key)
            else:
                new_key = f"{prefix}{key}"
                out[new_key] = value
                prefixed.append(key)

    return PrefixResult(env=out, prefixed=prefixed, skipped=skipped)
