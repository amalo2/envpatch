"""Tests for envpatch.linter."""
import pytest
from envpatch.linter import lint_env, LintResult, LintIssue


def test_lint_returns_lint_result():
    result = lint_env("KEY=value")
    assert isinstance(result, LintResult)


def test_clean_env_has_no_issues():
    result = lint_env("KEY=value\nOTHER=123")
    assert not result.has_issues


def test_blank_lines_and_comments_are_skipped():
    source = "# comment\n\nKEY=value"
    result = lint_env(source)
    assert not result.has_issues


def test_lowercase_key_triggers_warning():
    result = lint_env("mykey=value")
    assert result.has_issues
    assert any(i.key == "mykey" and "uppercase" in i.message for i in result.issues)


def test_lowercase_key_is_warning_severity():
    result = lint_env("mykey=value")
    issue = next(i for i in result.issues if "uppercase" in i.message)
    assert issue.severity == "warning"


def test_duplicate_key_triggers_error():
    source = "KEY=first\nKEY=second"
    result = lint_env(source)
    assert any("Duplicate" in i.message for i in result.issues)


def test_duplicate_key_is_error_severity():
    source = "KEY=first\nKEY=second"
    result = lint_env(source)
    issue = next(i for i in result.issues if "Duplicate" in i.message)
    assert issue.severity == "error"


def test_missing_equals_is_error():
    result = lint_env("BADLINE")
    assert result.error_count >= 1


def test_empty_value_triggers_warning():
    result = lint_env("KEY=")
    assert any("empty value" in i.message for i in result.issues)


def test_empty_value_is_warning_severity():
    result = lint_env("KEY=")
    issue = next(i for i in result.issues if "empty value" in i.message)
    assert issue.severity == "warning"


def test_key_with_space_is_error():
    result = lint_env("MY KEY=value")
    assert any("spaces" in i.message for i in result.issues)


def test_error_count_matches():
    source = "KEY=first\nKEY=second\nBADLINE"
    result = lint_env(source)
    assert result.error_count == 2


def test_warning_count_matches():
    source = "lower=val\nANOTHER="
    result = lint_env(source)
    assert result.warning_count == 2


def test_to_summary_no_issues():
    result = lint_env("KEY=value")
    assert result.to_summary() == "No lint issues found."


def test_to_summary_contains_issue_text():
    result = lint_env("lower=val")
    summary = result.to_summary()
    assert "lower" in summary
    assert "issue(s)" in summary


def test_issue_str_format():
    issue = LintIssue(line_number=3, key="FOO", message="something wrong", severity="error")
    text = str(issue)
    assert "ERROR" in text
    assert "line 3" in text
    assert "FOO" in text
