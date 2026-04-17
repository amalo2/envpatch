import pytest
from envpatch.cloner import clone_env, CloneResult

SOURCE = """DB_HOST=prod.db.local
DB_PORT=5432
SECRET_KEY=abc123
API_URL=https://api.example.com
"""

TARGET = """DB_HOST=localhost
APP_ENV=staging
"""


def test_clone_returns_clone_result():
    result = clone_env(SOURCE, TARGET)
    assert isinstance(result, CloneResult)


def test_new_keys_are_copied():
    result = clone_env(SOURCE, TARGET)
    assert "DB_PORT" in result.env
    assert result.env["DB_PORT"] == "5432"


def test_existing_keys_skipped_by_default():
    result = clone_env(SOURCE, TARGET)
    assert result.env["DB_HOST"] == "localhost"


def test_existing_keys_overwritten_when_flag_set():
    result = clone_env(SOURCE, TARGET, overwrite=True)
    assert result.env["DB_HOST"] == "prod.db.local"


def test_copied_count_incremented():
    result = clone_env(SOURCE, TARGET)
    assert result.copied_count >= 1


def test_skipped_count_incremented():
    result = clone_env(SOURCE, TARGET)
    assert result.skipped_count == 1


def test_overwritten_count_incremented():
    result = clone_env(SOURCE, TARGET, overwrite=True)
    assert result.overwritten_count == 1


def test_keys_filter_limits_cloned_keys():
    result = clone_env(SOURCE, TARGET, keys=["DB_PORT"])
    assert "DB_PORT" in result.env
    assert "SECRET_KEY" not in result.env


def test_remap_renames_key_in_target():
    result = clone_env(SOURCE, TARGET, keys=["API_URL"], remap={"API_URL": "EXTERNAL_API_URL"})
    assert "EXTERNAL_API_URL" in result.env
    assert "API_URL" not in result.env or result.env.get("API_URL") != "https://api.example.com"


def test_remap_tracked_in_result():
    result = clone_env(SOURCE, TARGET, keys=["API_URL"], remap={"API_URL": "EXTERNAL_API_URL"})
    assert result.remapped.get("API_URL") == "EXTERNAL_API_URL"


def test_target_only_keys_preserved():
    result = clone_env(SOURCE, TARGET)
    assert "APP_ENV" in result.env
    assert result.env["APP_ENV"] == "staging"


def test_summary_contains_counts():
    result = clone_env(SOURCE, TARGET)
    summary = result.to_summary()
    assert "Copied" in summary
    assert "Skipped" in summary
