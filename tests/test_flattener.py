import pytest
from envpatch.flattener import flatten_env, FlattenResult


SAMPLE = {
    "APP__HOST": "localhost",
    "APP__PORT": "8080",
    "DB__URL": "postgres://localhost/db",
    "SECRET": "abc123",
}


def test_flatten_returns_flatten_result():
    result = flatten_env(SAMPLE)
    assert isinstance(result, FlattenResult)


def test_all_keys_promoted_without_prefix():
    result = flatten_env(SAMPLE)
    assert result.promoted_count == len(SAMPLE)


def test_no_skipped_without_prefix():
    result = flatten_env(SAMPLE)
    assert result.skipped_count == 0


def test_prefix_filters_non_matching_keys():
    result = flatten_env(SAMPLE, prefix="APP")
    assert "HOST" in result.flattened
    assert "PORT" in result.flattened


def test_prefix_skips_non_matching_keys():
    result = flatten_env(SAMPLE, prefix="APP")
    assert "DB__URL" in result.skipped
    assert "SECRET" in result.skipped


def test_promoted_count_matches_prefix_keys():
    result = flatten_env(SAMPLE, prefix="APP")
    assert result.promoted_count == 2


def test_values_preserved():
    result = flatten_env(SAMPLE, prefix="APP")
    assert result.flattened["HOST"] == "localhost"
    assert result.flattened["PORT"] == "8080"


def test_uppercase_false_preserves_case():
    env = {"app__host": "localhost", "app__port": "8080"}
    result = flatten_env(env, prefix="app", uppercase=False)
    assert "host" in result.flattened
    assert "port" in result.flattened


def test_custom_separator():
    env = {"APP.HOST": "localhost", "APP.PORT": "9000"}
    result = flatten_env(env, prefix="APP", separator=".")
    assert "HOST" in result.flattened


def test_to_summary_contains_key_count():
    result = flatten_env(SAMPLE)
    summary = result.to_summary()
    assert str(len(SAMPLE)) in summary


def test_empty_short_key_is_skipped():
    env = {"APP__": "value"}
    result = flatten_env(env, prefix="APP")
    assert "APP__" in result.skipped
