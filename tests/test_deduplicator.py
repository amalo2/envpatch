"""Tests for envpatch.deduplicator."""

import pytest

from envpatch.deduplicator import DeduplicateResult, deduplicate_env


CLEAN_ENV = """HOST=localhost
PORT=5432
DEBUG=true
"""

DUPLICATE_ENV = """HOST=localhost
PORT=5432
HOST=remotehost
DEBUG=true
PORT=9999
"""


def test_deduplicate_returns_result():
    result = deduplicate_env(CLEAN_ENV)
    assert isinstance(result, DeduplicateResult)


def test_clean_env_has_no_resolved():
    result = deduplicate_env(CLEAN_ENV)
    assert result.resolved == []


def test_clean_env_is_clean():
    result = deduplicate_env(CLEAN_ENV)
    assert result.clean is True


def test_resolved_count_zero_for_clean_env():
    result = deduplicate_env(CLEAN_ENV)
    assert result.resolved_count == 0


def test_detects_duplicate_keys():
    result = deduplicate_env(DUPLICATE_ENV)
    assert "HOST" in result.resolved
    assert "PORT" in result.resolved


def test_resolved_count_matches_duplicates():
    result = deduplicate_env(DUPLICATE_ENV)
    assert result.resolved_count == 2


def test_keep_last_uses_final_value():
    result = deduplicate_env(DUPLICATE_ENV, keep="last")
    assert result.env["HOST"] == "remotehost"
    assert result.env["PORT"] == "9999"


def test_keep_first_uses_initial_value():
    result = deduplicate_env(DUPLICATE_ENV, keep="first")
    assert result.env["HOST"] == "localhost"
    assert result.env["PORT"] == "5432"


def test_non_duplicate_keys_preserved():
    result = deduplicate_env(DUPLICATE_ENV)
    assert result.env["DEBUG"] == "true"


def test_kept_lines_populated_for_duplicates():
    result = deduplicate_env(DUPLICATE_ENV, keep="last")
    assert "HOST" in result.kept_lines
    assert result.kept_lines["HOST"] == 3  # line 3 is the last HOST


def test_kept_lines_first_occurrence():
    result = deduplicate_env(DUPLICATE_ENV, keep="first")
    assert result.kept_lines["HOST"] == 1


def test_invalid_keep_raises_value_error():
    with pytest.raises(ValueError, match="keep must be"):
        deduplicate_env(CLEAN_ENV, keep="middle")


def test_to_summary_clean():
    result = deduplicate_env(CLEAN_ENV)
    assert result.to_summary() == "No duplicate keys found."


def test_to_summary_with_duplicates():
    result = deduplicate_env(DUPLICATE_ENV)
    summary = result.to_summary()
    assert "2" in summary
    assert "HOST" in summary
    assert "PORT" in summary


def test_quoted_values_stripped():
    env = 'KEY="hello"\nKEY=world\n'
    result = deduplicate_env(env, keep="first")
    assert result.env["KEY"] == "hello"


def test_comments_and_blank_lines_ignored():
    env = "# comment\n\nHOST=a\nHOST=b\n"
    result = deduplicate_env(env, keep="last")
    assert result.env["HOST"] == "b"
    assert result.resolved == ["HOST"]
