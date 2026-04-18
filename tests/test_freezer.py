import pytest
from envpatch.freezer import freeze_env, is_frozen, FreezeResult


SAMPLE_ENV = """DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=abc123
DEBUG=true
"""


def test_freeze_returns_freeze_result():
    result = freeze_env(SAMPLE_ENV)
    assert isinstance(result, FreezeResult)


def test_freeze_all_keys_by_default():
    result = freeze_env(SAMPLE_ENV)
    assert result.frozen_count == 4


def test_freeze_specific_keys():
    result = freeze_env(SAMPLE_ENV, keys=["DB_HOST", "SECRET_KEY"])
    assert "DB_HOST" in result.frozen_keys
    assert "SECRET_KEY" in result.frozen_keys


def test_skipped_keys_not_in_frozen():
    result = freeze_env(SAMPLE_ENV, keys=["DB_HOST"])
    assert "DB_PORT" in result.skipped_keys
    assert "DEBUG" in result.skipped_keys


def test_frozen_count_matches_keys_arg():
    result = freeze_env(SAMPLE_ENV, keys=["DB_HOST", "DB_PORT"])
    assert result.frozen_count == 2


def test_skipped_count_correct():
    result = freeze_env(SAMPLE_ENV, keys=["DB_HOST"])
    assert result.skipped_count == 3


def test_output_contains_marker():
    result = freeze_env(SAMPLE_ENV, keys=["DB_HOST"])
    output = result.frozen["__output__"]
    assert "# frozen" in output


def test_unfrozen_lines_unchanged():
    result = freeze_env(SAMPLE_ENV, keys=["DB_HOST"])
    output = result.frozen["__output__"]
    assert "DB_PORT=5432" in output


def test_is_frozen_detects_marker():
    assert is_frozen("DB_HOST=localhost  # frozen") is True


def test_is_frozen_returns_false_without_marker():
    assert is_frozen("DB_HOST=localhost") is False


def test_custom_marker_used():
    result = freeze_env(SAMPLE_ENV, keys=["DB_HOST"], marker="# locked")
    output = result.frozen["__output__"]
    assert "# locked" in output


def test_to_summary_contains_counts():
    result = freeze_env(SAMPLE_ENV, keys=["DB_HOST"])
    summary = result.to_summary()
    assert "Frozen:" in summary
    assert "Skipped:" in summary
