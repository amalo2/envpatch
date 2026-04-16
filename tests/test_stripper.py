"""Tests for envpatch.stripper."""
import pytest
from envpatch.stripper import strip_keys, StripResult

SAMPLE = """\
APP_NAME=myapp
APP_SECRET=s3cr3t
DB_HOST=localhost
DB_PASSWORD=hunter2
PORT=8080
"""


def test_strip_returns_strip_result():
    result = strip_keys(SAMPLE, keys=["PORT"])
    assert isinstance(result, StripResult)


def test_explicit_key_removed():
    result = strip_keys(SAMPLE, keys=["PORT"])
    assert "PORT" not in result.output


def test_explicit_key_in_stripped_list():
    result = strip_keys(SAMPLE, keys=["PORT"])
    assert "PORT" in result.stripped


def test_other_keys_preserved():
    result = strip_keys(SAMPLE, keys=["PORT"])
    assert "APP_NAME=myapp" in result.output


def test_pattern_removes_matching_keys():
    result = strip_keys(SAMPLE, patterns=[r"SECRET|PASSWORD"])
    assert "APP_SECRET" not in result.output
    assert "DB_PASSWORD" not in result.output


def test_pattern_stripped_list_populated():
    result = strip_keys(SAMPLE, patterns=[r"SECRET|PASSWORD"])
    assert "APP_SECRET" in result.stripped
    assert "DB_PASSWORD" in result.stripped


def test_non_matching_keys_kept():
    result = strip_keys(SAMPLE, patterns=[r"SECRET|PASSWORD"])
    assert "APP_NAME" in result.kept
    assert "DB_HOST" in result.kept


def test_stripped_count():
    result = strip_keys(SAMPLE, keys=["APP_NAME", "PORT"])
    assert result.stripped_count == 2


def test_kept_count():
    result = strip_keys(SAMPLE, keys=["PORT"])
    assert result.kept_count == len(result.kept)


def test_comments_preserved():
    env = "# comment\nKEY=val\nOTHER=x\n"
    result = strip_keys(env, keys=["KEY"])
    assert "# comment" in result.output


def test_blank_lines_preserved():
    env = "KEY=val\n\nOTHER=x\n"
    result = strip_keys(env, keys=["KEY"])
    assert "\n" in result.output


def test_no_keys_no_patterns_strips_nothing():
    result = strip_keys(SAMPLE)
    assert result.stripped_count == 0


def test_to_summary_string():
    result = strip_keys(SAMPLE, keys=["PORT"])
    summary = result.to_summary()
    assert "Stripped" in summary
    assert "kept" in summary
