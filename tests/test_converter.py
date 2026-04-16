"""Tests for envpatch.converter."""
import json
import pytest
from envpatch.converter import convert_env, from_json, dict_to_env, ConvertResult

SAMPLE = """DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=abc123
"""


def test_convert_returns_convert_result():
    result = convert_env(SAMPLE, "json")
    assert isinstance(result, ConvertResult)


def test_convert_json_is_parseable():
    result = convert_env(SAMPLE, "json")
    data = json.loads(result.output)
    assert isinstance(data, dict)


def test_convert_json_contains_keys():
    result = convert_env(SAMPLE, "json")
    data = json.loads(result.output)
    assert data["DB_HOST"] == "localhost"
    assert data["DB_PORT"] == "5432"


def test_key_count_matches():
    result = convert_env(SAMPLE, "json")
    assert result.key_count == 3


def test_fmt_field_set():
    result = convert_env(SAMPLE, "json")
    assert result.fmt == "json"


def test_unsupported_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        convert_env(SAMPLE, "xml")


def test_to_summary_contains_format():
    result = convert_env(SAMPLE, "json")
    summary = result.to_summary()
    assert "json" in summary


def test_to_summary_contains_key_count():
    result = convert_env(SAMPLE, "json")
    summary = result.to_summary()
    assert "3" in summary


def test_from_json_returns_env_string():
    data = {"FOO": "bar", "BAZ": "qux"}
    env = from_json(json.dumps(data))
    assert "FOO=bar" in env
    assert "BAZ=qux" in env


def test_from_json_rejects_non_object():
    with pytest.raises(ValueError):
        from_json(json.dumps(["not", "an", "object"]))


def test_dict_to_env_quotes_values_with_spaces():
    env = dict_to_env({"MSG": "hello world"})
    assert 'MSG="hello world"' in env


def test_dict_to_env_plain_values_unquoted():
    env = dict_to_env({"PORT": "8080"})
    assert "PORT=8080" in env


def test_empty_env_string_gives_zero_keys():
    result = convert_env("", "json")
    assert result.key_count == 0
    assert json.loads(result.output) == {}
