import pytest
from envpatch.prefixer import prefix_env, PrefixResult


SAMPLE = """HOST=localhost
PORT=5432
APP_NAME=myapp
"""


def test_prefix_returns_prefix_result():
    result = prefix_env(SAMPLE, "APP_")
    assert isinstance(result, PrefixResult)


def test_all_keys_prefixed_without_skip():
    result = prefix_env("HOST=localhost\nPORT=5432\n", "APP_", skip_existing=False)
    assert "APP_HOST" in result.env
    assert "APP_PORT" in result.env


def test_original_keys_removed_after_prefix():
    result = prefix_env("HOST=localhost\n", "APP_", skip_existing=False)
    assert "HOST" not in result.env


def test_values_preserved_after_prefix():
    result = prefix_env("HOST=localhost\n", "APP_", skip_existing=False)
    assert result.env["APP_HOST"] == "localhost"


def test_skip_existing_leaves_prefixed_keys_unchanged():
    result = prefix_env(SAMPLE, "APP_", skip_existing=True)
    assert "APP_NAME" in result.env
    assert result.env["APP_NAME"] == "myapp"


def test_skip_existing_records_skipped_key():
    result = prefix_env(SAMPLE, "APP_", skip_existing=True)
    assert "APP_NAME" in result.skipped


def test_prefixed_list_contains_new_keys():
    result = prefix_env("HOST=localhost\n", "APP_")
    assert "HOST" in result.prefixed


def test_prefixed_count_incremented():
    result = prefix_env("HOST=localhost\nPORT=5432\n", "APP_")
    assert result.prefixed_count == 2


def test_skipped_count_zero_when_no_existing_prefix():
    result = prefix_env("HOST=localhost\n", "APP_")
    assert result.skipped_count == 0


def test_strip_removes_prefix():
    result = prefix_env("APP_HOST=localhost\nAPP_PORT=5432\n", "APP_", strip=True)
    assert "HOST" in result.env
    assert "PORT" in result.env


def test_strip_removes_prefixed_keys():
    result = prefix_env("APP_HOST=localhost\n", "APP_", strip=True)
    assert "APP_HOST" not in result.env


def test_strip_skips_non_matching_keys():
    result = prefix_env("APP_HOST=localhost\nNAME=foo\n", "APP_", strip=True)
    assert "NAME" in result.env
    assert "NAME" in result.skipped


def test_to_summary_contains_counts():
    result = prefix_env(SAMPLE, "APP_")
    summary = result.to_summary()
    assert str(result.prefixed_count) in summary
    assert str(result.skipped_count) in summary
