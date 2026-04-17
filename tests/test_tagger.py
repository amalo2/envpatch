import pytest
from envpatch.tagger import tag_env, filter_by_tag, TagResult


SAMPLE_ENV = """
DB_HOST=localhost
DB_PASSWORD=secret123
AWS_ACCESS_KEY_ID=AKIA1234
APP_NAME=myapp
EMPTY_VAL=
API_TOKEN=tok_abc
"""


def test_tag_returns_tag_result():
    result = tag_env(SAMPLE_ENV)
    assert isinstance(result, TagResult)


def test_all_keys_tagged():
    result = tag_env(SAMPLE_ENV)
    assert set(result.tagged.keys()) == set(result.env.keys())


def test_sensitive_tag_on_password():
    result = tag_env(SAMPLE_ENV)
    assert "sensitive" in result.tagged["DB_PASSWORD"]


def test_sensitive_tag_on_token():
    result = tag_env(SAMPLE_ENV)
    assert "sensitive" in result.tagged["API_TOKEN"]


def test_database_tag_on_db_host():
    result = tag_env(SAMPLE_ENV)
    assert "database" in result.tagged["DB_HOST"]


def test_cloud_tag_on_aws_key():
    result = tag_env(SAMPLE_ENV)
    assert "cloud" in result.tagged["AWS_ACCESS_KEY_ID"]


def test_empty_tag_on_blank_value():
    result = tag_env(SAMPLE_ENV)
    assert "empty" in result.tagged["EMPTY_VAL"]


def test_general_tag_on_plain_key():
    result = tag_env(SAMPLE_ENV)
    assert "general" in result.tagged["APP_NAME"]


def test_tag_count_matches_keys():
    result = tag_env(SAMPLE_ENV)
    assert result.tag_count == len(result.env)


def test_filter_by_tag_sensitive():
    result = tag_env(SAMPLE_ENV)
    sensitive = filter_by_tag(result, "sensitive")
    assert "DB_PASSWORD" in sensitive
    assert "API_TOKEN" in sensitive
    assert "APP_NAME" not in sensitive


def test_filter_by_tag_returns_values():
    result = tag_env(SAMPLE_ENV)
    db_keys = filter_by_tag(result, "database")
    assert db_keys["DB_HOST"] == "localhost"


def test_extra_tags_applied():
    result = tag_env(SAMPLE_ENV, extra_tags={"APP_NAME": ["custom"]})
    assert "custom" in result.tagged["APP_NAME"]


def test_to_summary_contains_key():
    result = tag_env(SAMPLE_ENV)
    summary = result.to_summary()
    assert "DB_PASSWORD" in summary


def test_untagged_count_is_zero_when_all_tagged():
    result = tag_env(SAMPLE_ENV)
    assert result.untagged_count == 0


def test_network_tag_on_db_host():
    result = tag_env(SAMPLE_ENV)
    assert "network" in result.tagged["DB_HOST"]
