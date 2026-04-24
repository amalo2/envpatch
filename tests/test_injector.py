"""Tests for envpatch.injector."""
import pytest

from envpatch.injector import InjectResult, inject_env


SIMPLE_ENV = """DB_HOST=localhost
DB_PORT=5432
APP_SECRET=hunter2
"""


def test_inject_returns_inject_result():
    result = inject_env(SIMPLE_ENV, target={})
    assert isinstance(result, InjectResult)


def test_all_keys_injected_into_empty_target():
    target: dict = {}
    result = inject_env(SIMPLE_ENV, target=target)
    assert result.injected_count == 3


def test_injected_keys_present_in_target():
    target: dict = {}
    inject_env(SIMPLE_ENV, target=target)
    assert target["DB_HOST"] == "localhost"
    assert target["DB_PORT"] == "5432"


def test_existing_key_skipped_by_default():
    target = {"DB_HOST": "remotehost"}
    result = inject_env(SIMPLE_ENV, target=target)
    assert "DB_HOST" in result.skipped
    assert target["DB_HOST"] == "remotehost"


def test_existing_key_overwritten_when_flag_set():
    target = {"DB_HOST": "remotehost"}
    inject_env(SIMPLE_ENV, target=target, overwrite=True)
    assert target["DB_HOST"] == "localhost"


def test_skipped_count_correct():
    target = {"DB_HOST": "remotehost", "DB_PORT": "9999"}
    result = inject_env(SIMPLE_ENV, target=target)
    assert result.skipped_count == 2


def test_injected_list_contains_new_keys():
    target: dict = {}
    result = inject_env(SIMPLE_ENV, target=target)
    assert "DB_HOST" in result.injected
    assert "APP_SECRET" in result.injected


def test_prefix_applied_to_keys():
    target: dict = {}
    inject_env("FOO=bar\n", prefix="MY_", target=target)
    assert "MY_FOO" in target
    assert "FOO" not in target


def test_prefix_skips_existing_prefixed_key():
    target = {"MY_FOO": "original"}
    result = inject_env("FOO=bar\n", prefix="MY_", target=target)
    assert "MY_FOO" in result.skipped
    assert target["MY_FOO"] == "original"


def test_env_snapshot_in_result():
    target: dict = {}
    result = inject_env("X=1\n", target=target)
    assert result.env["X"] == "1"


def test_to_summary_string():
    target: dict = {}
    result = inject_env(SIMPLE_ENV, target=target)
    summary = result.to_summary()
    assert "3" in summary
    assert "skipped" in summary


def test_empty_env_string_injects_nothing():
    target: dict = {}
    result = inject_env("", target=target)
    assert result.injected_count == 0
    assert result.skipped_count == 0
