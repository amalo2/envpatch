import pytest
from envpatch.scoper import scope_env, ScopeResult

SAMPLE = """
DB_HOST=localhost
DB_PORT=5432
AWS_ACCESS_KEY=abc123
AWS_SECRET=supersecret
APP_ENV=production
APP_DEBUG=false
"""


def test_scope_returns_scope_result():
    result = scope_env(SAMPLE, "db")
    assert isinstance(result, ScopeResult)


def test_scope_name_stored():
    result = scope_env(SAMPLE, "db")
    assert result.scope == "db"


def test_db_keys_included():
    result = scope_env(SAMPLE, "db")
    assert "DB_HOST" in result.included
    assert "DB_PORT" in result.included


def test_non_db_keys_excluded():
    result = scope_env(SAMPLE, "db")
    assert "AWS_ACCESS_KEY" in result.excluded
    assert "APP_ENV" in result.excluded


def test_included_count_correct():
    result = scope_env(SAMPLE, "db")
    assert result.included_count == 2


def test_excluded_count_correct():
    result = scope_env(SAMPLE, "db")
    assert result.excluded_count == 4


def test_env_dict_contains_included_keys():
    result = scope_env(SAMPLE, "db")
    assert "DB_HOST" in result.env
    assert result.env["DB_HOST"] == "localhost"


def test_strip_prefix_removes_prefix():
    result = scope_env(SAMPLE, "db", strip_prefix=True)
    assert "HOST" in result.env
    assert "PORT" in result.env
    assert "DB_HOST" not in result.env


def test_strip_prefix_preserves_values():
    result = scope_env(SAMPLE, "db", strip_prefix=True)
    assert result.env["HOST"] == "localhost"
    assert result.env["PORT"] == "5432"


def test_custom_prefixes_used():
    result = scope_env(SAMPLE, "cloud", prefixes=["AWS_"])
    assert "AWS_ACCESS_KEY" in result.included
    assert "AWS_SECRET" in result.included


def test_custom_prefix_excludes_others():
    result = scope_env(SAMPLE, "cloud", prefixes=["AWS_"])
    assert "DB_HOST" in result.excluded


def test_to_summary_contains_scope():
    result = scope_env(SAMPLE, "app")
    summary = result.to_summary()
    assert "app" in summary


def test_to_summary_contains_counts():
    result = scope_env(SAMPLE, "app")
    summary = result.to_summary()
    assert str(result.included_count) in summary
    assert str(result.excluded_count) in summary
