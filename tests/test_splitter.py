"""Tests for envpatch.splitter."""
import pytest

from envpatch.splitter import SplitResult, split_env

SAMPLE_ENV = """
DB_HOST=localhost
DB_PORT=5432
AWS_ACCESS_KEY=AKIAIOSFODNN7
AWS_SECRET_KEY=wJalrXUtnFEMI
APP_DEBUG=true
PORT=8080
""".strip()


def test_split_returns_split_result():
    result = split_env(SAMPLE_ENV, ["DB_", "AWS_"])
    assert isinstance(result, SplitResult)


def test_db_keys_in_db_segment():
    result = split_env(SAMPLE_ENV, ["DB_", "AWS_"])
    assert "DB_HOST" in result.segments["DB_"]
    assert "DB_PORT" in result.segments["DB_"]


def test_aws_keys_in_aws_segment():
    result = split_env(SAMPLE_ENV, ["DB_", "AWS_"])
    assert "AWS_ACCESS_KEY" in result.segments["AWS_"]
    assert "AWS_SECRET_KEY" in result.segments["AWS_"]


def test_unmatched_keys_captured():
    result = split_env(SAMPLE_ENV, ["DB_", "AWS_"])
    assert "PORT" in result.unmatched
    assert "APP_DEBUG" in result.unmatched


def test_unmatched_excluded_when_flag_false():
    result = split_env(SAMPLE_ENV, ["DB_", "AWS_"], keep_unmatched=False)
    assert result.unmatched == {}


def test_strip_prefix_removes_prefix_from_keys():
    result = split_env(SAMPLE_ENV, ["DB_"], strip_prefix=True)
    assert "HOST" in result.segments["DB_"]
    assert "PORT" in result.segments["DB_"]
    assert "DB_HOST" not in result.segments["DB_"]


def test_values_preserved_after_split():
    result = split_env(SAMPLE_ENV, ["DB_"])
    assert result.segments["DB_"]["DB_HOST"] == "localhost"
    assert result.segments["DB_"]["DB_PORT"] == "5432"


def test_segment_count():
    result = split_env(SAMPLE_ENV, ["DB_", "AWS_"])
    assert result.segment_count == 2


def test_total_keys_includes_unmatched():
    result = split_env(SAMPLE_ENV, ["DB_", "AWS_"])
    assert result.total_keys == 6


def test_total_keys_without_unmatched():
    result = split_env(SAMPLE_ENV, ["DB_", "AWS_"], keep_unmatched=False)
    assert result.total_keys == 4


def test_to_summary_contains_segment_name():
    result = split_env(SAMPLE_ENV, ["DB_", "AWS_"])
    summary = result.to_summary()
    assert "DB_" in summary
    assert "AWS_" in summary


def test_to_summary_contains_key_count():
    result = split_env(SAMPLE_ENV, ["DB_", "AWS_"])
    summary = result.to_summary()
    assert "2 key(s)" in summary


def test_empty_segment_when_no_match():
    result = split_env(SAMPLE_ENV, ["REDIS_"])
    assert result.segments["REDIS_"] == {}
