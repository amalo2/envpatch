"""Tests for envpatch.renamer."""

import pytest
from envpatch.renamer import rename_keys, RenameResult


SAMPLE_ENV = """APP_NAME=myapp
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=abc123
"""


def test_rename_returns_rename_result():
    result = rename_keys(SAMPLE_ENV, {"APP_NAME": "APPLICATION_NAME"})
    assert isinstance(result, RenameResult)


def test_renamed_key_appears_in_output():
    result = rename_keys(SAMPLE_ENV, {"APP_NAME": "APPLICATION_NAME"})
    assert "APPLICATION_NAME=myapp" in result.output


def test_old_key_removed_from_output():
    result = rename_keys(SAMPLE_ENV, {"APP_NAME": "APPLICATION_NAME"})
    assert "APP_NAME=" not in result.output


def test_renamed_list_contains_old_key():
    result = rename_keys(SAMPLE_ENV, {"APP_NAME": "APPLICATION_NAME"})
    assert "APP_NAME" in result.renamed


def test_renamed_count_incremented():
    result = rename_keys(SAMPLE_ENV, {"APP_NAME": "APPLICATION_NAME", "DB_HOST": "DATABASE_HOST"})
    assert result.renamed_count == 2


def test_missing_key_is_skipped():
    result = rename_keys(SAMPLE_ENV, {"MISSING_KEY": "NEW_KEY"})
    assert "MISSING_KEY" in result.skipped


def test_skipped_count_incremented_for_missing():
    result = rename_keys(SAMPLE_ENV, {"MISSING_KEY": "NEW_KEY"})
    assert result.skipped_count == 1


def test_existing_target_key_skips_rename_by_default():
    env = "OLD_KEY=value\nNEW_KEY=other\n"
    result = rename_keys(env, {"OLD_KEY": "NEW_KEY"})
    assert "OLD_KEY" in result.skipped


def test_overwrite_existing_allows_rename():
    env = "OLD_KEY=value\nNEW_KEY=other\n"
    result = rename_keys(env, {"OLD_KEY": "NEW_KEY"}, overwrite_existing=True)
    assert "OLD_KEY" in result.renamed


def test_comments_preserved_in_output():
    env = "# comment\nAPP=val\n"
    result = rename_keys(env, {"APP": "APPLICATION"})
    assert "# comment" in result.output


def test_blank_lines_preserved_in_output():
    env = "APP=val\n\nDB=host\n"
    result = rename_keys(env, {})
    assert "\n\n" in result.output


def test_unrelated_keys_unchanged():
    result = rename_keys(SAMPLE_ENV, {"APP_NAME": "APPLICATION_NAME"})
    assert "DB_HOST=localhost" in result.output


def test_to_summary_contains_counts():
    result = rename_keys(SAMPLE_ENV, {"APP_NAME": "APPLICATION_NAME", "MISSING": "X"})
    summary = result.to_summary()
    assert "Renamed: 1" in summary
    assert "Skipped: 1" in summary


def test_value_with_equals_preserved():
    env = "ENCODED=abc=def==\n"
    result = rename_keys(env, {"ENCODED": "B64_VALUE"})
    assert "B64_VALUE=abc=def==" in result.output
