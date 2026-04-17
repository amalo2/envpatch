"""Tests for envpatch.requirer."""
import pytest
from envpatch.requirer import require_keys, RequireResult

SAMPLE = """
DB_HOST=localhost
DB_PORT=5432
APP_SECRET=abc123
"""


def test_require_returns_require_result():
    result = require_keys(SAMPLE, ["DB_HOST"])
    assert isinstance(result, RequireResult)


def test_all_present_is_satisfied():
    result = require_keys(SAMPLE, ["DB_HOST", "DB_PORT"])
    assert result.is_satisfied


def test_missing_key_not_satisfied():
    result = require_keys(SAMPLE, ["DB_HOST", "MISSING_KEY"])
    assert not result.is_satisfied


def test_present_list_contains_found_keys():
    result = require_keys(SAMPLE, ["DB_HOST", "DB_PORT"])
    assert "DB_HOST" in result.present
    assert "DB_PORT" in result.present


def test_missing_list_contains_absent_keys():
    result = require_keys(SAMPLE, ["DB_HOST", "NO_SUCH_KEY"])
    assert "NO_SUCH_KEY" in result.missing


def test_present_count_matches():
    result = require_keys(SAMPLE, ["DB_HOST", "DB_PORT", "NOPE"])
    assert result.present_count == 2


def test_missing_count_matches():
    result = require_keys(SAMPLE, ["DB_HOST", "NOPE1", "NOPE2"])
    assert result.missing_count == 2


def test_required_list_preserved():
    keys = ["DB_HOST", "APP_SECRET"]
    result = require_keys(SAMPLE, keys)
    assert result.required == keys


def test_empty_required_list_is_satisfied():
    result = require_keys(SAMPLE, [])
    assert result.is_satisfied


def test_to_summary_contains_counts():
    result = require_keys(SAMPLE, ["DB_HOST", "MISSING"])
    summary = result.to_summary()
    assert "Required" in summary
    assert "Missing" in summary


def test_to_summary_lists_missing_keys():
    result = require_keys(SAMPLE, ["DB_HOST", "GHOST_KEY"])
    summary = result.to_summary()
    assert "GHOST_KEY" in summary


def test_env_dict_populated():
    result = require_keys(SAMPLE, ["DB_HOST"])
    assert result.env.get("DB_HOST") == "localhost"
