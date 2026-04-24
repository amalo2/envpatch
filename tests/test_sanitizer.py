"""Tests for envpatch.sanitizer."""

import pytest

from envpatch.sanitizer import SanitizeResult, sanitize_env


CLEAN_ENV = "FOO=hello\nBAR=world\nBAZ=123\n"
DIRTY_ENV = "FOO=hel\x00lo\nBAR=wor\x01ld\nBAZ=clean\n"


def test_sanitize_returns_sanitize_result():
    result = sanitize_env(CLEAN_ENV)
    assert isinstance(result, SanitizeResult)


def test_clean_env_has_no_sanitized_keys():
    result = sanitize_env(CLEAN_ENV)
    assert result.sanitized_count == 0


def test_clean_env_all_keys_skipped():
    result = sanitize_env(CLEAN_ENV)
    assert result.skipped_count == 3


def test_dirty_value_is_cleaned():
    result = sanitize_env(DIRTY_ENV)
    assert result.env["FOO"] == "hello"


def test_control_char_removed_by_default():
    result = sanitize_env("KEY=ab\x01cd\n")
    assert result.env["KEY"] == "abcd"


def test_null_byte_removed():
    result = sanitize_env("KEY=ab\x00cd\n")
    assert result.env["KEY"] == "abcd"


def test_sanitized_key_in_sanitized_list():
    result = sanitize_env(DIRTY_ENV)
    assert "FOO" in result.sanitized
    assert "BAR" in result.sanitized


def test_clean_key_in_skipped_list():
    result = sanitize_env(DIRTY_ENV)
    assert "BAZ" in result.skipped


def test_sanitized_count_matches_dirty_keys():
    result = sanitize_env(DIRTY_ENV)
    assert result.sanitized_count == 2


def test_replacement_char_used_when_provided():
    result = sanitize_env("KEY=ab\x01cd\n", replacement="?")
    assert result.env["KEY"] == "ab?cd"


def test_keys_filter_limits_processing():
    result = sanitize_env(DIRTY_ENV, keys=["FOO"])
    assert "FOO" in result.sanitized
    assert "BAR" not in result.sanitized


def test_keys_filter_skips_unselected():
    result = sanitize_env(DIRTY_ENV, keys=["FOO"])
    assert "BAR" in result.skipped


def test_values_preserved_when_clean():
    result = sanitize_env(CLEAN_ENV)
    assert result.env["FOO"] == "hello"
    assert result.env["BAR"] == "world"


def test_to_summary_returns_string():
    result = sanitize_env(DIRTY_ENV)
    summary = result.to_summary()
    assert isinstance(summary, str)
    assert "Sanitized" in summary


def test_to_summary_contains_counts():
    result = sanitize_env(DIRTY_ENV)
    summary = result.to_summary()
    assert "2" in summary
