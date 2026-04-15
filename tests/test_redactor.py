"""Tests for envpatch.redactor module."""

import pytest
from envpatch.redactor import (
    is_sensitive,
    redact_value,
    redact_env,
    redact_diff_changes,
    REDACTED_PLACEHOLDER,
    DEFAULT_SENSITIVE_PATTERNS,
)
from envpatch.differ import EnvChange


# --- is_sensitive ---

def test_is_sensitive_matches_secret():
    assert is_sensitive("MY_SECRET") is True


def test_is_sensitive_matches_password():
    assert is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_matches_token():
    assert is_sensitive("AUTH_TOKEN") is True


def test_is_sensitive_matches_api_key():
    assert is_sensitive("STRIPE_API_KEY") is True


def test_is_sensitive_returns_false_for_safe_key():
    assert is_sensitive("APP_ENV") is False


def test_is_sensitive_case_insensitive():
    assert is_sensitive("db_password") is True


def test_is_sensitive_custom_patterns():
    assert is_sensitive("INTERNAL_KEY", patterns=[r".*INTERNAL.*"]) is True


def test_is_sensitive_custom_patterns_no_match():
    assert is_sensitive("MY_SECRET", patterns=[r".*INTERNAL.*"]) is False


# --- redact_value ---

def test_redact_value_masks_sensitive():
    result = redact_value("DB_PASSWORD", "s3cr3t")
    assert result == REDACTED_PLACEHOLDER


def test_redact_value_passes_through_safe():
    result = redact_value("APP_ENV", "production")
    assert result == "production"


# --- redact_env ---

def test_redact_env_masks_sensitive_keys():
    env = {"APP_ENV": "production", "DB_PASSWORD": "s3cr3t", "AUTH_TOKEN": "abc123"}
    result = redact_env(env)
    assert result["APP_ENV"] == "production"
    assert result["DB_PASSWORD"] == REDACTED_PLACEHOLDER
    assert result["AUTH_TOKEN"] == REDACTED_PLACEHOLDER


def test_redact_env_returns_new_dict():
    env = {"APP_ENV": "staging"}
    result = redact_env(env)
    assert result is not env


def test_redact_env_empty_input():
    assert redact_env({}) == {}


# --- redact_diff_changes ---

def test_redact_diff_changes_masks_new_value():
    changes = [EnvChange(key="DB_PASSWORD", old_value=None, new_value="newpass")]
    result = redact_diff_changes(changes)
    assert result[0].new_value == REDACTED_PLACEHOLDER


def test_redact_diff_changes_masks_old_value():
    changes = [EnvChange(key="AUTH_TOKEN", old_value="oldtoken", new_value="newtoken")]
    result = redact_diff_changes(changes)
    assert result[0].old_value == REDACTED_PLACEHOLDER
    assert result[0].new_value == REDACTED_PLACEHOLDER


def test_redact_diff_changes_preserves_safe_keys():
    changes = [EnvChange(key="APP_ENV", old_value="staging", new_value="production")]
    result = redact_diff_changes(changes)
    assert result[0].old_value == "staging"
    assert result[0].new_value == "production"


def test_redact_diff_changes_handles_none_values():
    changes = [EnvChange(key="MY_SECRET", old_value=None, new_value="secret")]
    result = redact_diff_changes(changes)
    assert result[0].old_value is None
    assert result[0].new_value == REDACTED_PLACEHOLDER
