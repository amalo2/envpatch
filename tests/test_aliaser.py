import pytest
from envpatch.aliaser import alias_keys, AliasResult


SAMPLE_ENV = {
    "DATABASE_URL": "postgres://localhost/db",
    "APP_SECRET": "supersecret",
    "PORT": "8080",
}


def test_alias_returns_alias_result():
    result = alias_keys(SAMPLE_ENV, {})
    assert isinstance(result, AliasResult)


def test_aliased_key_appears_in_env():
    result = alias_keys(SAMPLE_ENV, {"DATABASE_URL": "DB_URL"})
    assert "DB_URL" in result.env


def test_aliased_value_matches_source():
    result = alias_keys(SAMPLE_ENV, {"DATABASE_URL": "DB_URL"})
    assert result.env["DB_URL"] == SAMPLE_ENV["DATABASE_URL"]


def test_source_key_still_present():
    result = alias_keys(SAMPLE_ENV, {"DATABASE_URL": "DB_URL"})
    assert "DATABASE_URL" in result.env


def test_aliased_list_contains_source_key():
    result = alias_keys(SAMPLE_ENV, {"DATABASE_URL": "DB_URL"})
    assert "DATABASE_URL" in result.aliased


def test_aliased_count_incremented():
    result = alias_keys(SAMPLE_ENV, {"DATABASE_URL": "DB_URL", "PORT": "APP_PORT"})
    assert result.aliased_count == 2


def test_missing_source_key_is_skipped():
    result = alias_keys(SAMPLE_ENV, {"NONEXISTENT": "NEW_KEY"})
    assert "NONEXISTENT" in result.skipped
    assert "NEW_KEY" not in result.env


def test_existing_alias_key_skipped_by_default():
    env = {**SAMPLE_ENV, "DB_URL": "existing"}
    result = alias_keys(env, {"DATABASE_URL": "DB_URL"})
    assert "DATABASE_URL" in result.skipped
    assert result.env["DB_URL"] == "existing"


def test_existing_alias_key_overwritten_when_flag_set():
    env = {**SAMPLE_ENV, "DB_URL": "existing"}
    result = alias_keys(env, {"DATABASE_URL": "DB_URL"}, overwrite=True)
    assert result.env["DB_URL"] == SAMPLE_ENV["DATABASE_URL"]


def test_skipped_count_correct():
    result = alias_keys(SAMPLE_ENV, {"NONEXISTENT": "NEW_KEY"})
    assert result.skipped_count == 1


def test_to_summary_contains_counts():
    result = alias_keys(SAMPLE_ENV, {"DATABASE_URL": "DB_URL", "NONEXISTENT": "X"})
    summary = result.to_summary()
    assert "1" in summary
    assert "Aliased" in summary
    assert "Skipped" in summary


def test_empty_aliases_returns_unchanged_env():
    result = alias_keys(SAMPLE_ENV, {})
    assert result.env == SAMPLE_ENV
    assert result.aliased_count == 0
