"""Tests for envpatch.defaults."""
import pytest

from envpatch.defaults import apply_defaults, DefaultsResult


TARGET = """APP_NAME=myapp
DEBUG=true
"""

DEFAULTS = """APP_NAME=defaultapp
DEBUG=false
LOG_LEVEL=info
PORT=8080
"""


def test_apply_defaults_returns_defaults_result():
    result = apply_defaults(TARGET, DEFAULTS)
    assert isinstance(result, DefaultsResult)


def test_missing_keys_are_filled():
    result = apply_defaults(TARGET, DEFAULTS)
    assert "LOG_LEVEL" in result.filled
    assert "PORT" in result.filled


def test_existing_keys_not_overwritten_by_default():
    result = apply_defaults(TARGET, DEFAULTS)
    assert result.filled["APP_NAME"] == "myapp"
    assert result.filled["DEBUG"] == "true"


def test_existing_keys_in_skipped_list():
    result = apply_defaults(TARGET, DEFAULTS)
    assert "APP_NAME" in result.skipped
    assert "DEBUG" in result.skipped


def test_applied_list_contains_new_keys():
    result = apply_defaults(TARGET, DEFAULTS)
    assert "LOG_LEVEL" in result.applied
    assert "PORT" in result.applied


def test_filled_count_matches_applied():
    result = apply_defaults(TARGET, DEFAULTS)
    assert result.filled_count == len(result.applied)


def test_skipped_count_matches_skipped():
    result = apply_defaults(TARGET, DEFAULTS)
    assert result.skipped_count == len(result.skipped)


def test_overwrite_flag_replaces_existing_keys():
    result = apply_defaults(TARGET, DEFAULTS, overwrite=True)
    assert result.filled["APP_NAME"] == "defaultapp"
    assert result.filled["DEBUG"] == "false"


def test_overwrite_applied_list_includes_changed_keys():
    result = apply_defaults(TARGET, DEFAULTS, overwrite=True)
    assert "APP_NAME" in result.applied
    assert "DEBUG" in result.applied


def test_to_summary_returns_string():
    result = apply_defaults(TARGET, DEFAULTS)
    summary = result.to_summary()
    assert isinstance(summary, str)
    assert "filled" in summary


def test_empty_target_fills_all_defaults():
    result = apply_defaults("", DEFAULTS)
    assert result.filled_count == 4
    assert result.skipped_count == 0


def test_empty_defaults_changes_nothing():
    result = apply_defaults(TARGET, "")
    assert result.filled_count == 0
    assert set(result.filled.keys()) == {"APP_NAME", "DEBUG"}
