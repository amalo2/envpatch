"""Linter for .env files — checks for style and best-practice issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envpatch.parser import parse_env_string


@dataclass
class LintIssue:
    line_number: int
    key: str
    message: str
    severity: str = "warning"  # 'warning' | 'error'

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] line {self.line_number}: {self.key} — {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")

    def to_summary(self) -> str:
        if not self.has_issues:
            return "No lint issues found."
        lines = [str(issue) for issue in self.issues]
        lines.append(
            f"\n{len(self.issues)} issue(s): {self.error_count} error(s), {self.warning_count} warning(s)."
        )
        return "\n".join(lines)


def lint_env(source: str) -> LintResult:
    """Run lint checks on a raw .env string and return a LintResult."""
    result = LintResult()
    seen_keys: dict[str, int] = {}

    for lineno, raw_line in enumerate(source.splitlines(), start=1):
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            result.issues.append(
                LintIssue(lineno, "", "Line missing '=' separator", severity="error")
            )
            continue

        key, _, value = line.partition("=""")
        key = key.strip()

        if key != key.upper():
            result.issues.append(
                LintIssue(lineno, key, "Key is not uppercase", severity="warning")
            )

        if " " in key:
            result.issues.append(
                LintIssue(lineno, key, "Key contains spaces", severity="error")
            )

        if key in seen_keys:
            result.issues.append(
                LintIssue(
                    lineno,
                    key,
                    f"Duplicate key (first seen on line {seen_keys[key]})",
                    severity="error",
                )
            )
        else:
            seen_keys[key] = lineno

        stripped_value = value.strip()
        if stripped_value == "":
            result.issues.append(
                LintIssue(lineno, key, "Key has an empty value", severity="warning")
            )

    return result
