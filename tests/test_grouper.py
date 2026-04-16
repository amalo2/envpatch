import pytest
from envpatch.grouper import group_env, filter_group, GroupResult


SAMPLE_ENV = """
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
AWS_KEY=abc123
AWS_SECRET=xyz
PORT=8080
DEBUG=true
"""


def test_group_returns_group_result():
    result = group_env(SAMPLE_ENV)
    assert isinstance(result, GroupResult)


def test_key_count_matches_total():
    result = group_env(SAMPLE_ENV)
    assert result.key_count == 7


def test_db_keys_grouped():
    result = group_env(SAMPLE_ENV)
    assert "DB" in result.groups
    assert len(result.groups["DB"]) == 3


def test_aws_keys_grouped():
    result = group_env(SAMPLE_ENV)
    assert "AWS" in result.groups
    assert "AWS_KEY" in result.groups["AWS"]
    assert "AWS_SECRET" in result.groups["AWS"]


def test_ungrouped_keys_captured():
    result = group_env(SAMPLE_ENV)
    assert "PORT" in result.ungrouped
    assert "DEBUG" in result.ungrouped


def test_group_count():
    result = group_env(SAMPLE_ENV)
    assert result.group_count() == 2


def test_values_preserved():
    result = group_env(SAMPLE_ENV)
    assert result.groups["DB"]["DB_HOST"] == "localhost"
    assert result.groups["DB"]["DB_PORT"] == "5432"


def test_custom_delimiter():
    env = "APP.NAME=foo\nAPP.ENV=prod\nPORT=80"
    result = group_env(env, delimiter=".")
    assert "APP" in result.groups
    assert len(result.groups["APP"]) == 2
    assert "PORT" in result.ungrouped


def test_filter_group_returns_dict():
    result = group_env(SAMPLE_ENV)
    db = filter_group(result, "DB")
    assert isinstance(db, dict)
    assert "DB_HOST" in db


def test_filter_group_missing_returns_none():
    result = group_env(SAMPLE_ENV)
    assert filter_group(result, "MISSING") is None


def test_to_summary_contains_group_names():
    result = group_env(SAMPLE_ENV)
    summary = result.to_summary()
    assert "DB" in summary
    assert "AWS" in summary


def test_to_summary_shows_key_count():
    result = group_env(SAMPLE_ENV)
    summary = result.to_summary()
    assert "7" in summary


def test_empty_env_returns_empty_result():
    result = group_env("")
    assert result.key_count == 0
    assert result.group_count() == 0
    assert result.ungrouped == {}
