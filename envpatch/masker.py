from dataclasses import dataclass, field
from typing import Dict, List
from envpatch.redactor import is_sensitive


@dataclass
class MaskResult:
    masked: Dict[str, str] = field(default_factory=dict)
    mask_char: str = "*"
    masked_keys: List[str] = field(default_factory=list)
    visible_keys: List[str] = field(default_factory=list)

    @property
    def masked_count(self) -> int:
        return len(self.masked_keys)

    @property
    def visible_count(self) -> int:
        return len(self.visible_keys)

    def to_summary(self) -> str:
        return (
            f"Masked {self.masked_count} sensitive key(s), "
            f"{self.visible_count} key(s) visible."
        )


def _mask_value(value: str, mask_char: str = "*", reveal: int = 0) -> str:
    if not value:
        return value
    if reveal <= 0 or reveal >= len(value):
        return mask_char * max(len(value), 6)
    return value[:reveal] + mask_char * (len(value) - reveal)


def mask_env(
    env: Dict[str, str],
    mask_char: str = "*",
    reveal: int = 0,
    extra_patterns: List[str] | None = None,
) -> MaskResult:
    result = MaskResult(mask_char=mask_char)
    for key, value in env.items():
        if is_sensitive(key, extra_patterns=extra_patterns):
            result.masked[key] = _mask_value(value, mask_char=mask_char, reveal=reveal)
            result.masked_keys.append(key)
        else:
            result.masked[key] = value
            result.visible_keys.append(key)
    return result
