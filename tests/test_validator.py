"""Tests for envpatch.validator module."""

import pytest
from envpatch.validator import (
    validate_env_string,
    validate_env_dict,
    ValidationResult,
    ValidationError,
)


def test_valid_env_string_passes():
    content = "DB_HOST=localhost\nDB_PORT=5432\n# a comment\n"
    result = validate_env_string(content)
    assert result.is_valid


def test_missing_equals_is_error():
    content = "INVALID_LINE\n"
    result = validate_env_string(content)
    assert not result.is_valid
    assert len(result.errors) == 1
    assert result.errors[0].line_number == 1
    assert "missing '='" in result.errors[0].message


def test_invalid_key_name_is_error():
    content = "123INVALID=value\n"
    result = validate_env_string(content)
    assert not result.is_valid
    assert result.errors[0].key == "123INVALID"


def test_empty_key_is_error():
    content = "=value\n"
    result = validate_env_string(content)
    assert not result.is_valid
    assert "empty key" in result.errors[0].message


def test_blank_lines_and_comments_are_skipped():
    content = "\n# comment\n   \n"
    result = validate_env_string(content)
    assert result.is_valid


def test_multiple_errors_reported():
    content = "GOOD=ok\n123BAD=x\nNO_EQUALS\n"
    result = validate_env_string(content)
    assert not result.is_valid
    assert len(result.errors) == 2


def test_validate_env_dict_valid():
    env = {"APP_NAME": "myapp", "_PRIVATE": "secret", "Port": "8080"}
    result = validate_env_dict(env)
    assert result.is_valid


def test_validate_env_dict_invalid_key():
    env = {"GOOD_KEY": "ok", "bad-key": "nope"}
    result = validate_env_dict(env)
    assert not result.is_valid
    assert result.errors[0].key == "bad-key"


def test_validation_result_str_on_pass():
    result = ValidationResult()
    assert "passed" in str(result)


def test_validation_result_str_on_fail():
    result = ValidationResult()
    result.add_error("something wrong", line_number=3, key="BAD")
    summary = str(result)
    assert "1 error" in summary
    assert "line 3" in summary
    assert "BAD" in summary


def test_validation_error_str_formats_correctly():
    err = ValidationError(line_number=5, key="X", message="oops")
    assert str(err) == "line 5: key 'X': oops"


def test_validation_error_str_without_optional_fields():
    err = ValidationError(line_number=None, key=None, message="generic error")
    assert str(err) == "generic error"
