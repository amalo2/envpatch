"""Variable interpolation for .env files."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

_VAR_RE = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolateResult:
    output: Dict[str, str]
    resolved: List[str] = field(default_factory=list)
    unresolved: List[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return len(self.unresolved) == 0

    def to_summary(self) -> str:
        lines = [
            f"Resolved references : {len(self.resolved)}",
            f"Unresolved references: {len(self.unresolved)}",
        ]
        if self.unresolved:
            lines.append("Missing: " + ", ".join(self.unresolved))
        return "\n".join(lines)


def interpolate_env(
    env: Dict[str, str],
    context: Optional[Dict[str, str]] = None,
    strict: bool = False,
) -> InterpolateResult:
    """Expand $VAR / ${VAR} references in values using env itself + optional context."""
    lookup: Dict[str, str] = {}
    if context:
        lookup.update(context)
    lookup.update(env)

    output: Dict[str, str] = {}
    resolved: List[str] = []
    unresolved: List[str] = []

    for key, value in env.items():
        def replacer(m: re.Match) -> str:
            ref = m.group(1) or m.group(2)
            if ref in lookup:
                if ref not in resolved:
                    resolved.append(ref)
                return lookup[ref]
            if ref not in unresolved:
                unresolved.append(ref)
            if strict:
                raise KeyError(f"Unresolved variable: ${ref}")
            return m.group(0)

        output[key] = _VAR_RE.sub(replacer, value)

    return InterpolateResult(output=output, resolved=resolved, unresolved=unresolved)
