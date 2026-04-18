import pytest
from envpatch.normalizer import normalize_env, NormalizeResult


def test_normalize_returns_result():
    result = normalize_env("FOO=bar")
    assert isinstance(result, NormalizeResult)


def test_lowercase_key_is_uppercased():
    result = normalize_env("foo=bar")
    assert "FOO" in result.output


def test_lowercase_key_in_normalized_list():
    result = normalize_env("foo=bar")
    assert "foo" in result.normalized


def test_already_uppercase_key_is_skipped():
    result = normalize_env("FOO=bar")
    assert "FOO" in result.skipped


def test_hyphen_replaced_with_underscore():
    result = normalize_env("MY-KEY=val")
    assert "MY_KEY" in result.output


def test_hyphen_key_counted_as_normalized():
    result = normalize_env("MY-KEY=val")
    assert "MY-KEY" in result.normalized


def test_value_preserved_after_normalization():
    result = normalize_env("foo=hello world")
    assert result.output["FOO"] == "hello world"


def test_normalized_count():
    result = normalize_env("foo=1\nBAR=2\nbaz-key=3")
    assert result.normalized_count == 2


def test_skipped_count():
    result = normalize_env("foo=1\nBAR=2\nbaz-key=3")
    assert result.skipped_count == 1


def test_to_summary_contains_counts():
    result = normalize_env("foo=1\nBAR=2")
    summary = result.to_summary()
    assert "1" in summary
    assert "Normalized" in summary


def test_multiple_keys_all_uppercased():
    result = normalize_env("a=1\nb=2\nc=3")
    assert set(result.output.keys()) == {"A", "B", "C"}


def test_empty_string_returns_empty_result():
    result = normalize_env("")
    assert result.output == {}
    assert result.normalized_count == 0
    assert result.skipped_count == 0
