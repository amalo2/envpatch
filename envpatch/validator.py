"""Validation utilities for .env files and patch operations."""

from dataclasses import dataclass, field
from typing import List, Optional
import re

KEY_PATTERN = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


@dataclass
class ValidationError:
    line_number: Optional[int]
    key: Optional[str]
    message: str

    def __str__(self) -> str:
        parts = []
        if self.line_number is not None:
            parts.append(f"line {self.line_number}")
        if self.key is not None:
            parts.append(f"key '{self.key}'")
        parts.append(self.message)
        return ": ".join(parts)


@dataclass
class ValidationResult:
    errors: List[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, message: str, line_number: Optional[int] = None, key: Optional[str] = None) -> None:
        self.errors.append(ValidationError(line_number=line_number, key=key, message=message))

    def __str__(self) -> str:
        if self.is_valid:
            return "Validation passed."
        lines = [f"Validation failed with {len(self.errors)} error(s):"]
        for error in self.errors:
            lines.append(f"  - {error}")
        return "\n".join(lines)


def validate_env_string(content: str) -> ValidationResult:
    """Validate raw .env file content, returning a ValidationResult."""
    result = ValidationResult()
    for lineno, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            result.add_error("missing '=' separator", line_number=lineno)
            continue
        key, _, _ = line.partition("=")
        key = key.strip()
        if not key:
            result.add_error("empty key", line_number=lineno)
        elif not KEY_PATTERN.match(key):
            result.add_error(
                f"invalid key name '{key}' (must match [A-Za-z_][A-Za-z0-9_]*)",
                line_number=lineno,
                key=key,
            )
    return result


def validate_env_dict(env: dict) -> ValidationResult:
    """Validate a parsed env dictionary for key naming conventions."""
    result = ValidationResult()
    for key in env:
        if not KEY_PATTERN.match(key):
            result.add_error(f"invalid key name", key=key)
    return result
