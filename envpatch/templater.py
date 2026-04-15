"""Template rendering for .env files — substitute variables and generate env files from templates."""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_VAR_PATTERN = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)(?::([^}]*))?\}")


@dataclass
class RenderResult:
    output: str
    resolved: List[str] = field(default_factory=list)
    unresolved: List[str] = field(default_factory=list)
    used_defaults: List[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return len(self.unresolved) == 0

    def to_summary(self) -> str:
        lines = []
        if self.resolved:
            lines.append(f"Resolved: {', '.join(self.resolved)}")
        if self.used_defaults:
            lines.append(f"Defaulted: {', '.join(self.used_defaults)}")
        if self.unresolved:
            lines.append(f"Unresolved: {', '.join(self.unresolved)}")
        return "\n".join(lines) if lines else "No variables found."


def render_template(template: str, context: Dict[str, str], strict: bool = False) -> RenderResult:
    """Render a .env template by substituting ${VAR} or ${VAR:default} placeholders.

    Args:
        template: Raw template string containing ${VAR} placeholders.
        context: Dictionary of variable names to values.
        strict: If True, raise ValueError on unresolved variables.

    Returns:
        RenderResult with rendered output and metadata.
    """
    result = RenderResult(output="")
    seen: Dict[str, str] = {}

    def replacer(match: re.Match) -> str:
        key = match.group(1)
        default: Optional[str] = match.group(2)

        if key in context:
            result.resolved.append(key)
            seen[key] = context[key]
            return context[key]
        elif default is not None:
            result.used_defaults.append(key)
            return default
        else:
            result.unresolved.append(key)
            if strict:
                raise ValueError(f"Unresolved template variable: {key}")
            return match.group(0)

    result.output = _VAR_PATTERN.sub(replacer, template)
    return result


def render_template_file(template_path: str, context: Dict[str, str], strict: bool = False) -> RenderResult:
    """Read a template file and render it with the given context."""
    with open(template_path, "r") as fh:
        template = fh.read()
    return render_template(template, context, strict=strict)
