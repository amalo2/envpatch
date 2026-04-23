"""Tests for envpatch.rotator."""
import pytest

from envpatch.rotator import RotateResult, rotate_keys

SAMPLE_ENV = """
DB_PASSWORD=old_password
API_KEY=old_api_key
APP_NAME=myapp
""".strip()


def test_rotate_returns_rotate_result():
    result = rotate_keys(SAMPLE_ENV, keys=["DB_PASSWORD"])
    assert isinstance(result, RotateResult)


def test_rotated_key_value_changes():
    result = rotate_keys(SAMPLE_ENV, keys=["DB_PASSWORD"])
    assert result.env["DB_PASSWORD"] != "old_password"


def test_rotated_key_in_rotated_list():
    result = rotate_keys(SAMPLE_ENV, keys=["DB_PASSWORD"])
    assert "DB_PASSWORD" in result.rotated


def test_unrotated_key_value_unchanged():
    result = rotate_keys(SAMPLE_ENV, keys=["DB_PASSWORD"])
    assert result.env["APP_NAME"] == "myapp"


def test_multiple_keys_rotated():
    result = rotate_keys(SAMPLE_ENV, keys=["DB_PASSWORD", "API_KEY"])
    assert result.rotated_count == 2
    assert result.env["DB_PASSWORD"] != "old_password"
    assert result.env["API_KEY"] != "old_api_key"


def test_missing_key_skipped_by_default():
    result = rotate_keys(SAMPLE_ENV, keys=["NONEXISTENT_KEY"])
    assert "NONEXISTENT_KEY" in result.skipped
    assert result.skipped_count == 1


def test_missing_key_raises_when_skip_missing_false():
    with pytest.raises(KeyError, match="NONEXISTENT_KEY"):
        rotate_keys(SAMPLE_ENV, keys=["NONEXISTENT_KEY"], skip_missing=False)


def test_rotated_count_incremented():
    result = rotate_keys(SAMPLE_ENV, keys=["DB_PASSWORD", "API_KEY"])
    assert result.rotated_count == 2


def test_skipped_count_zero_when_all_present():
    result = rotate_keys(SAMPLE_ENV, keys=["DB_PASSWORD"])
    assert result.skipped_count == 0


def test_custom_generator_used():
    result = rotate_keys(SAMPLE_ENV, keys=["DB_PASSWORD"], generator=lambda: "FIXED")
    assert result.env["DB_PASSWORD"] == "FIXED"


def test_generated_secret_length_respected():
    result = rotate_keys(SAMPLE_ENV, keys=["DB_PASSWORD"], length=16)
    assert len(result.env["DB_PASSWORD"]) == 16


def test_to_summary_contains_counts():
    result = rotate_keys(SAMPLE_ENV, keys=["DB_PASSWORD", "NONEXISTENT_KEY"])
    summary = result.to_summary()
    assert "1" in summary
    assert "Rotated" in summary
    assert "skipped" in summary


def test_env_dict_contains_all_original_keys():
    result = rotate_keys(SAMPLE_ENV, keys=["DB_PASSWORD"])
    assert "API_KEY" in result.env
    assert "APP_NAME" in result.env
    assert "DB_PASSWORD" in result.env
