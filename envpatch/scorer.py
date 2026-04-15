"""Env file quality scorer — produces a numeric score based on linting, profiling, and validation."""
from dataclasses import dataclass, field
from typing import List

from envpatch.linter import lint_env, LintResult
from envpatch.profiler import profile_env, ProfileResult
from envpatch.validator import validate_env_string, ValidationResult


@dataclass
class ScoreResult:
    total_keys: int
    score: int  # 0-100
    penalties: List[str] = field(default_factory=list)
    lint: LintResult = None
    profile: ProfileResult = None
    validation: ValidationResult = None

    @property
    def grade(self) -> str:
        if self.score >= 90:
            return "A"
        elif self.score >= 75:
            return "B"
        elif self.score >= 60:
            return "C"
        elif self.score >= 40:
            return "D"
        return "F"

    def to_summary(self) -> str:
        lines = [
            f"Score : {self.score}/100 (Grade: {self.grade})",
            f"Keys  : {self.total_keys}",
        ]
        if self.penalties:
            lines.append("Penalties:")
            for p in self.penalties:
                lines.append(f"  - {p}")
        return "\n".join(lines)


def score_env(env_string: str) -> ScoreResult:
    """Analyse an env string and return a quality score."""
    validation = validate_env_string(env_string)
    lint = lint_env(env_string)
    profile = profile_env(env_string)

    score = 100
    penalties: List[str] = []

    # Validation errors: -15 each, capped at -45
    val_penalty = min(len(validation.errors) * 15, 45)
    if val_penalty:
        score -= val_penalty
        penalties.append(f"{len(validation.errors)} validation error(s) (-{val_penalty})")

    # Lint errors: -10 each, capped at -30
    lint_errors = lint.error_count
    lint_penalty = min(lint_errors * 10, 30)
    if lint_penalty:
        score -= lint_penalty
        penalties.append(f"{lint_errors} lint error(s) (-{lint_penalty})")

    # Lint warnings: -3 each, capped at -15
    lint_warnings = lint.warning_count
    warn_penalty = min(lint_warnings * 3, 15)
    if warn_penalty:
        score -= warn_penalty
        penalties.append(f"{lint_warnings} lint warning(s) (-{warn_penalty})")

    # Blank values: -2 each, capped at -10
    blank_penalty = min(profile.blank_count * 2, 10)
    if blank_penalty:
        score -= blank_penalty
        penalties.append(f"{profile.blank_count} blank value(s) (-{blank_penalty})")

    score = max(score, 0)

    return ScoreResult(
        total_keys=profile.total_keys,
        score=score,
        penalties=penalties,
        lint=lint,
        profile=profile,
        validation=validation,
    )
