import pytest
from envpatch.pinner import pin_env, serialize_pinned, PinResult

SAMPLE = """DB_HOST=localhost
DB_PASS=secret
APP_ENV=production
API_KEY=abc123
"""


def test_pin_returns_pin_result():
    result = pin_env(SAMPLE, ["DB_HOST"])
    assert isinstance(result, PinResult)


def test_pinned_key_in_result():
    result = pin_env(SAMPLE, ["DB_HOST"])
    assert "DB_HOST" in result.pinned


def test_pinned_count_incremented():
    result = pin_env(SAMPLE, ["DB_HOST", "API_KEY"])
    assert result.pinned_count == 2


def test_unpinned_keys_not_in_pinned():
    result = pin_env(SAMPLE, ["DB_HOST"])
    assert "APP_ENV" not in result.pinned


def test_already_pinned_key_skipped_by_default():
    env = "DB_HOST=localhost  # pinned\n"
    result = pin_env(env, ["DB_HOST"])
    assert "DB_HOST" in result.skipped
    assert result.skipped_count == 1


def test_already_pinned_key_overwritten_when_flag_set():
    env = "DB_HOST=localhost  # pinned\n"
    result = pin_env(env, ["DB_HOST"], overwrite=True)
    assert "DB_HOST" not in result.skipped
    assert result.pinned_count == 1


def test_source_keys_populated():
    result = pin_env(SAMPLE, [])
    assert "DB_HOST" in result.source_keys
    assert "APP_ENV" in result.source_keys


def test_to_summary_string():
    result = pin_env(SAMPLE, ["DB_HOST"])
    summary = result.to_summary()
    assert "Pinned" in summary
    assert "skipped" in summary


def test_serialize_pinned_contains_marker():
    output = serialize_pinned(SAMPLE, ["DB_HOST"])
    assert "DB_HOST=localhost  # pinned" in output


def test_serialize_pinned_leaves_others_unchanged():
    output = serialize_pinned(SAMPLE, ["DB_HOST"])
    assert "APP_ENV=production" in output


def test_serialize_pinned_multiple_keys():
    output = serialize_pinned(SAMPLE, ["DB_HOST", "API_KEY"])
    assert "# pinned" in output
    lines_with_marker = [l for l in output.splitlines() if "# pinned" in l]
    assert len(lines_with_marker) == 2


def test_custom_marker_used():
    output = serialize_pinned(SAMPLE, ["DB_HOST"], marker="# locked")
    assert "# locked" in output
    assert "# pinned" not in output
