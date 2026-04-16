"""Tests for envpatch.trimmer."""
import pytest
from envpatch.trimmer import TrimResult, trim_env


DIRTY_ENV = "KEY1=  hello  \nKEY2=world\nKEY3=\t spaced \t\n"
CLEAN_ENV = "KEY1=hello\nKEY2=world\n"


def test_trim_returns_trim_result():
    result = trim_env(DIRTY_ENV)
    assert isinstance(result, TrimResult)


def test_trimmed_values_have_no_surrounding_whitespace():
    result = trim_env(DIRTY_ENV)
    from envpatch.parser import parse_env_string
    parsed = parse_env_string(result.output)
    assert parsed["KEY1"] == "hello"
    assert parsed["KEY3"] == "spaced"


def test_clean_values_unchanged():
    result = trim_env(DIRTY_ENV)
    from envpatch.parser import parse_env_string
    parsed = parse_env_string(result.output)
    assert parsed["KEY2"] == "world"


def test_trimmed_list_contains_dirty_keys():
    result = trim_env(DIRTY_ENV)
    assert "KEY1" in result.trimmed
    assert "KEY3" in result.trimmed


def test_skipped_list_contains_clean_keys():
    result = trim_env(DIRTY_ENV)
    assert "KEY2" in result.skipped


def test_trimmed_count():
    result = trim_env(DIRTY_ENV)
    assert result.trimmed_count == 2


def test_skipped_count():
    result = trim_env(DIRTY_ENV)
    assert result.skipped_count == 1


def test_clean_env_has_zero_trimmed():
    result = trim_env(CLEAN_ENV)
    assert result.trimmed_count == 0


def test_selective_trim_only_affects_specified_keys():
    result = trim_env(DIRTY_ENV, keys=["KEY1"])
    assert "KEY1" in result.trimmed
    assert "KEY3" not in result.trimmed


def test_selective_trim_leaves_unspecified_keys_untouched():
    result = trim_env(DIRTY_ENV, keys=["KEY1"])
    from envpatch.parser import parse_env_string
    parsed = parse_env_string(result.output)
    assert parsed["KEY3"] == "\t spaced \t"


def test_to_summary_returns_string():
    result = trim_env(DIRTY_ENV)
    summary = result.to_summary()
    assert isinstance(summary, str)
    assert "2" in summary
