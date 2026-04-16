from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

TYPE_PATTERNS = {
    "bool": re.compile(r"^(true|false|1|0|yes|no)$", re.IGNORECASE),
    "int": re.compile(r"^-?\d+$"),
    "float": re.compile(r"^-?\d+\.\d+$"),
    "url": re.compile(r"^https?://\S+$"),
    "email": re.compile(r"^[\w.+-]+@[\w-]+\.[\w.]+$"),
    "uuid": re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE),
}


@dataclass
class TypeHint:
    key: str
    value: str
    detected: Optional[str]

    def is_typed(self) -> bool:
        return self.detected is not None


@dataclass
class TypeCheckResult:
    hints: List[TypeHint] = field(default_factory=list)
    untyped: List[str] = field(default_factory=list)

    @property
    def typed_count(self) -> int:
        return len(self.hints)

    @property
    def untyped_count(self) -> int:
        return len(self.untyped)

    def to_summary(self) -> str:
        lines = [f"Typed: {self.typed_count}  Untyped: {self.untyped_count}"]
        for h in self.hints:
            lines.append(f"  {h.key}: {h.detected}")
        if self.untyped:
            lines.append("Untyped keys: " + ", ".join(self.untyped))
        return "\n".join(lines)


def detect_type(value: str) -> Optional[str]:
    for type_name, pattern in TYPE_PATTERNS.items():
        if pattern.match(value):
            return type_name
    return None


def typecheck_env(env: Dict[str, str]) -> TypeCheckResult:
    result = TypeCheckResult()
    for key, value in env.items():
        detected = detect_type(value)
        if detected:
            result.hints.append(TypeHint(key=key, value=value, detected=detected))
        else:
            result.untyped.append(key)
    return result
