"""Tests for envpatch.parser."""

import pytest
from envpatch.parser import parse_env_string, _parse_value


SAMPLE_ENV = """
# Database config
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb  # production database

SECRET_KEY="super secret value"
ANOTHER='single quoted'
EMPTY_VAL=
SPACED_VAL=  hello world  
"""


def test_basic_key_value():
    result = parse_env_string("FOO=bar")
    assert result == {"FOO": "bar"}


def test_skips_comments():
    result = parse_env_string("# comment\nFOO=bar")
    assert "#" not in "".join(result.keys())
    assert result == {"FOO": "bar"}


def test_skips_blank_lines():
    result = parse_env_string("\n\nFOO=bar\n\n")
    assert result == {"FOO": "bar"}


def test_double_quoted_value():
    result = parse_env_string('SECRET_KEY="super secret value"')
    assert result["SECRET_KEY"] == "super secret value"


def test_single_quoted_value():
    result = parse_env_string("ANOTHER='single quoted'")
    assert result["ANOTHER"] == "single quoted"


def test_inline_comment_stripped():
    result = parse_env_string("DB_NAME=mydb  # production database")
    assert result["DB_NAME"] == "mydb"


def test_empty_value():
    result = parse_env_string("EMPTY_VAL=")
    assert result["EMPTY_VAL"] == ""


def test_full_sample():
    result = parse_env_string(SAMPLE_ENV)
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"
    assert result["DB_NAME"] == "mydb"
    assert result["SECRET_KEY"] == "super secret value"
    assert result["ANOTHER"] == "single quoted"
    assert result["EMPTY_VAL"] == ""


def test_invalid_lines_ignored():
    content = "VALID=yes\nnot-valid-line\n123INVALID=nope"
    result = parse_env_string(content)
    assert list(result.keys()) == ["VALID"]


@pytest.mark.parametrize("raw,expected", [
    ('"hello"', 'hello'),
    ("'world'", 'world'),
    ('plain', 'plain'),
    ('value # comment', 'value'),
    ('', ''),
])
def test_parse_value(raw, expected):
    assert _parse_value(raw) == expected
