"""Tests for envpatch.merger module."""

import pytest
from envpatch.merger import merge_envs, merge_env_strings, MergeResult


BASE_ENV = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "development"}
INCOMING_ENV = {"DB_HOST": "prod.db.example.com", "DB_PORT": "5433", "NEW_KEY": "new_value"}


def test_merge_result_is_returned():
    result = merge_envs(BASE_ENV, INCOMING_ENV)
    assert isinstance(result, MergeResult)


def test_new_keys_are_applied():
    result = merge_envs(BASE_ENV, INCOMING_ENV)
    assert "NEW_KEY" in result.merged
    assert result.merged["NEW_KEY"] == "new_value"


def test_existing_keys_are_skipped_by_default():
    result = merge_envs(BASE_ENV, INCOMING_ENV)
    assert result.merged["DB_HOST"] == "localhost"
    assert result.merged["DB_PORT"] == "5432"


def test_existing_keys_overwritten_when_flag_set():
    result = merge_envs(BASE_ENV, INCOMING_ENV, overwrite=True)
    assert result.merged["DB_HOST"] == "prod.db.example.com"
    assert result.merged["DB_PORT"] == "5433"


def test_applied_list_contains_new_keys():
    result = merge_envs(BASE_ENV, INCOMING_ENV)
    applied_keys = [c.key for c in result.applied]
    assert "NEW_KEY" in applied_keys


def test_skipped_list_contains_existing_keys():
    result = merge_envs(BASE_ENV, INCOMING_ENV)
    skipped_keys = [c.key for c in result.skipped]
    assert "DB_HOST" in skipped_keys
    assert "DB_PORT" in skipped_keys


def test_base_only_keys_preserved():
    result = merge_envs(BASE_ENV, INCOMING_ENV)
    assert result.merged["APP_ENV"] == "development"


def test_applied_count_and_skipped_count():
    result = merge_envs(BASE_ENV, INCOMING_ENV)
    assert result.applied_count == 1
    assert result.skipped_count == 2


def test_merge_with_specific_keys_only():
    result = merge_envs(BASE_ENV, INCOMING_ENV, overwrite=True, keys=["DB_HOST"])
    assert result.merged["DB_HOST"] == "prod.db.example.com"
    assert result.merged["DB_PORT"] == "5432"  # not in keys, not overwritten
    assert "NEW_KEY" not in result.merged  # not in keys, not applied


def test_merge_env_strings():
    base_str = "DB_HOST=localhost\nAPP_ENV=development\n"
    incoming_str = "DB_HOST=prod.example.com\nNEW_KEY=hello\n"
    result = merge_env_strings(base_str, incoming_str)
    assert result.merged["DB_HOST"] == "localhost"
    assert result.merged["NEW_KEY"] == "hello"
    assert result.merged["APP_ENV"] == "development"


def test_summary_contains_applied_and_skipped():
    result = merge_envs(BASE_ENV, INCOMING_ENV)
    summary = result.to_summary()
    assert "Applied" in summary
    assert "Skipped" in summary
    assert "NEW_KEY" in summary


def test_summary_no_changes():
    result = merge_envs({"A": "1"}, {"A": "2"})
    summary = result.to_summary()
    assert "No changes applied" not in summary  # skipped is still reported
    assert "Skipped" in summary


def test_empty_incoming_no_changes():
    result = merge_envs(BASE_ENV, {})
    assert result.merged == BASE_ENV
    assert result.applied_count == 0
    assert result.skipped_count == 0
