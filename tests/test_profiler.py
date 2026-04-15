"""Tests for envpatch.profiler."""
import pytest

from envpatch.profiler import profile_env, ProfileResult


SAMPLE_ENV = {
    "APP_NAME": "myapp",
    "APP_SECRET": "supersecret",
    "DATABASE_PASSWORD": "dbpass",
    "DEBUG": "",
    "PORT": "8080",
    "REPLICA_PORT": "8080",
    "LONG_KEY_NAME_EXAMPLE": "short",
    "X": "a" * 200,
}


def test_profile_returns_profile_result():
    result = profile_env(SAMPLE_ENV)
    assert isinstance(result, ProfileResult)


def test_total_keys_count():
    result = profile_env(SAMPLE_ENV)
    assert result.total_keys == len(SAMPLE_ENV)


def test_sensitive_keys_detected():
    result = profile_env(SAMPLE_ENV)
    assert "APP_SECRET" in result.sensitive_keys
    assert "DATABASE_PASSWORD" in result.sensitive_keys


def test_non_sensitive_key_excluded():
    result = profile_env(SAMPLE_ENV)
    assert "APP_NAME" not in result.sensitive_keys
    assert "PORT" not in result.sensitive_keys


def test_blank_value_keys_detected():
    result = profile_env(SAMPLE_ENV)
    assert "DEBUG" in result.blank_value_keys


def test_blank_value_keys_excludes_non_blank():
    result = profile_env(SAMPLE_ENV)
    assert "PORT" not in result.blank_value_keys


def test_duplicate_values_detected():
    result = profile_env(SAMPLE_ENV)
    # PORT and REPLICA_PORT share value "8080"
    assert "8080" in result.duplicate_values
    assert set(result.duplicate_values["8080"]) == {"PORT", "REPLICA_PORT"}


def test_empty_string_not_in_duplicate_values():
    result = profile_env(SAMPLE_ENV)
    assert "" not in result.duplicate_values


def test_longest_key():
    result = profile_env(SAMPLE_ENV)
    assert result.longest_key == "LONG_KEY_NAME_EXAMPLE"


def test_longest_value_key():
    result = profile_env(SAMPLE_ENV)
    assert result.longest_value_key == "X"


def test_sensitive_count_property():
    result = profile_env(SAMPLE_ENV)
    assert result.sensitive_count == len(result.sensitive_keys)


def test_blank_count_property():
    result = profile_env(SAMPLE_ENV)
    assert result.blank_count == len(result.blank_value_keys)


def test_to_summary_contains_totals():
    result = profile_env(SAMPLE_ENV)
    summary = result.to_summary()
    assert str(result.total_keys) in summary
    assert str(result.sensitive_count) in summary


def test_empty_env_returns_zero_totals():
    result = profile_env({})
    assert result.total_keys == 0
    assert result.sensitive_count == 0
    assert result.blank_count == 0
    assert result.duplicate_values == {}
