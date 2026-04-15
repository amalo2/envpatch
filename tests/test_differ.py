"""Tests for envpatch.differ."""

import pytest
from envpatch.differ import diff_envs, DiffResult, EnvChange


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}
TARGET = {"HOST": "prod.example.com", "PORT": "5432", "LOG_LEVEL": "info"}


def test_diff_returns_diff_result():
    result = diff_envs(BASE, TARGET)
    assert isinstance(result, DiffResult)


def test_detects_added_keys():
    result = diff_envs(BASE, TARGET)
    added_keys = {c.key for c in result.added}
    assert "LOG_LEVEL" in added_keys


def test_detects_removed_keys():
    result = diff_envs(BASE, TARGET)
    removed_keys = {c.key for c in result.removed}
    assert "DEBUG" in removed_keys


def test_detects_modified_keys():
    result = diff_envs(BASE, TARGET)
    modified_keys = {c.key for c in result.modified}
    assert "HOST" in modified_keys


def test_unchanged_keys_excluded_by_default():
    result = diff_envs(BASE, TARGET)
    unchanged_keys = {c.key for c in result.unchanged}
    assert "PORT" not in unchanged_keys


def test_unchanged_keys_included_when_requested():
    result = diff_envs(BASE, TARGET, include_unchanged=True)
    unchanged_keys = {c.key for c in result.unchanged}
    assert "PORT" in unchanged_keys


def test_modified_change_stores_old_and_new_value():
    result = diff_envs(BASE, TARGET)
    host_change = next(c for c in result.modified if c.key == "HOST")
    assert host_change.old_value == "localhost"
    assert host_change.new_value == "prod.example.com"


def test_added_change_has_no_old_value():
    result = diff_envs(BASE, TARGET)
    log_change = next(c for c in result.added if c.key == "LOG_LEVEL")
    assert log_change.old_value is None
    assert log_change.new_value == "info"


def test_removed_change_has_no_new_value():
    result = diff_envs(BASE, TARGET)
    debug_change = next(c for c in result.removed if c.key == "DEBUG")
    assert debug_change.new_value is None
    assert debug_change.old_value == "false"


def test_has_changes_true_when_diffs_exist():
    result = diff_envs(BASE, TARGET)
    assert result.has_changes() is True


def test_has_changes_false_for_identical_envs():
    result = diff_envs(BASE, BASE)
    assert result.has_changes() is False


def test_summary_describes_changes():
    result = diff_envs(BASE, TARGET)
    summary = result.summary()
    assert "added" in summary
    assert "removed" in summary
    assert "modified" in summary


def test_summary_no_changes():
    result = diff_envs(BASE, BASE)
    assert result.summary() == "no changes"


def test_env_change_str_added():
    change = EnvChange("FOO", "added", new_value="bar")
    assert str(change) == "+ FOO=bar"


def test_env_change_str_removed():
    change = EnvChange("FOO", "removed", old_value="bar")
    assert str(change) == "- FOO=bar"


def test_env_change_str_modified():
    change = EnvChange("FOO", "modified", old_value="old", new_value="new")
    assert "~" in str(change) and "FOO" in str(change)


def test_empty_base_all_added():
    result = diff_envs({}, {"A": "1", "B": "2"})
    assert len(result.added) == 2
    assert not result.removed
    assert not result.modified


def test_empty_target_all_removed():
    result = diff_envs({"A": "1", "B": "2"}, {})
    assert len(result.removed) == 2
    assert not result.added
    assert not result.modified
