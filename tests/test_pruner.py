"""Tests for envpatch.pruner."""
import pytest

from envpatch.pruner import PruneResult, prune_env


CLEAN_ENV = """DB_HOST=localhost
DB_PORT=5432
APP_NAME=myapp
"""

DIRTY_ENV = """DB_HOST=localhost
DB_PASSWORD=
API_KEY=<YOUR_API_KEY>
SECRET=changeme
TOKEN=null
APP_NAME=myapp
PLACEHOLDER=[fill me]
"""


def test_prune_returns_prune_result():
    result = prune_env(CLEAN_ENV)
    assert isinstance(result, PruneResult)


def test_clean_env_has_no_pruned_keys():
    result = prune_env(CLEAN_ENV)
    assert result.pruned_count == 0


def test_clean_env_kept_count_matches_total():
    result = prune_env(CLEAN_ENV)
    assert result.kept_count == 3


def test_empty_value_is_pruned():
    result = prune_env(DIRTY_ENV)
    assert "DB_PASSWORD" in result.pruned


def test_angle_bracket_placeholder_is_pruned():
    result = prune_env(DIRTY_ENV)
    assert "API_KEY" in result.pruned


def test_changeme_is_pruned():
    result = prune_env(DIRTY_ENV)
    assert "SECRET" in result.pruned


def test_null_value_is_pruned():
    result = prune_env(DIRTY_ENV)
    assert "TOKEN" in result.pruned


def test_bracket_placeholder_is_pruned():
    result = prune_env(DIRTY_ENV)
    assert "PLACEHOLDER" in result.pruned


def test_real_value_is_kept():
    result = prune_env(DIRTY_ENV)
    assert "DB_HOST" in result.kept
    assert "DB_HOST" in result.env


def test_pruned_key_absent_from_env():
    result = prune_env(DIRTY_ENV)
    for key in result.pruned:
        assert key not in result.env


def test_kept_count_and_pruned_count_sum_to_total():
    result = prune_env(DIRTY_ENV)
    parsed_total = result.kept_count + result.pruned_count
    assert parsed_total == 7


def test_extra_patterns_respected():
    env = "CUSTOM_KEY=REPLACE_ME\nSAFE=hello\n"
    result = prune_env(env, extra_patterns=[r"^REPLACE_ME$"])
    assert "CUSTOM_KEY" in result.pruned
    assert "SAFE" in result.kept


def test_keys_filter_limits_pruning():
    result = prune_env(DIRTY_ENV, keys=["DB_PASSWORD"])
    # Only DB_PASSWORD should be considered for pruning
    assert "DB_PASSWORD" in result.pruned
    # API_KEY has a placeholder value but was not in the keys list
    assert "API_KEY" in result.kept


def test_to_summary_contains_counts():
    result = prune_env(DIRTY_ENV)
    summary = result.to_summary()
    assert str(result.pruned_count) in summary
    assert str(result.kept_count) in summary
