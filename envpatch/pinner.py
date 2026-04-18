from dataclasses import dataclass, field
from typing import Dict, List
from envpatch.parser import parse_env_string


@dataclass
class PinResult:
    pinned: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    source_keys: List[str] = field(default_factory=list)

    @property
    def pinned_count(self) -> int:
        return len(self.pinned)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    def to_summary(self) -> str:
        return (
            f"Pinned {self.pinned_count} key(s), "
            f"skipped {self.skipped_count} key(s)."
        )


def pin_env(
    env_string: str,
    keys: List[str],
    marker: str = "# pinned",
    overwrite: bool = False,
) -> PinResult:
    """Mark specific keys as pinned by appending a comment marker inline."""
    parsed = parse_env_string(env_string)
    result = PinResult(source_keys=list(parsed.keys()))

    output: Dict[str, str] = {}
    for k, v in parsed.items():
        if k in keys:
            already_pinned = marker in v
            if already_pinned and not overwrite:
                result.skipped.append(k)
                output[k] = v
            else:
                clean_v = v.replace(marker, "").strip()
                output[k] = f"{clean_v}  {marker}"
                result.pinned[k] = output[k]
        else:
            output[k] = v

    result.pinned = {k: output[k] for k in keys if k in output and k not in result.skipped}
    return result


def serialize_pinned(env_string: str, keys: List[str], marker: str = "# pinned") -> str:
    """Return env string with pinned markers applied."""
    parsed = parse_env_string(env_string)
    lines = []
    for k, v in parsed.items():
        if k in keys:
            clean_v = v.replace(marker, "").strip()
            lines.append(f"{k}={clean_v}  {marker}")
        else:
            lines.append(f"{k}={v}")
    return "\n".join(lines)
