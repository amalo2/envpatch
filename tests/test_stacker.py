"""Tests for envpatch.stacker."""
import pytest

from envpatch.stacker import StackResult, stack_envs


BASE = "DB_HOST=localhost\nDB_PORT=5432\nAPP_ENV=development\n"
OVERRIDE = "DB_HOST=prod.db.example.com\nAPP_ENV=production\n"
EXTRA = "NEW_KEY=hello\n"


def test_stack_returns_stack_result():
    result = stack_envs([BASE])
    assert isinstance(result, StackResult)


def test_single_layer_has_all_keys():
    result = stack_envs([BASE], ["base"])
    assert "DB_HOST" in result.env
    assert "DB_PORT" in result.env
    assert "APP_ENV" in result.env


def test_later_layer_overrides_earlier():
    result = stack_envs([BASE, OVERRIDE], ["base", "override"])
    assert result.env["DB_HOST"] == "prod.db.example.com"
    assert result.env["APP_ENV"] == "production"


def test_non_overridden_keys_preserved():
    result = stack_envs([BASE, OVERRIDE], ["base", "override"])
    assert result.env["DB_PORT"] == "5432"


def test_extra_layer_adds_new_keys():
    result = stack_envs([BASE, OVERRIDE, EXTRA], ["base", "override", "extra"])
    assert "NEW_KEY" in result.env
    assert result.env["NEW_KEY"] == "hello"


def test_layer_count_matches_input():
    result = stack_envs([BASE, OVERRIDE], ["base", "override"])
    assert result.layer_count == 2


def test_total_keys_correct():
    result = stack_envs([BASE, OVERRIDE], ["base", "override"])
    # BASE has 3 keys; OVERRIDE redefines 2, adds 0 new
    assert result.total_keys == 3


def test_override_count_reflects_overridden_keys():
    result = stack_envs([BASE, OVERRIDE], ["base", "override"])
    # DB_HOST and APP_ENV are each overridden once
    assert result.override_count == 2


def test_overrides_dict_contains_overridden_key():
    result = stack_envs([BASE, OVERRIDE], ["base", "override"])
    assert "DB_HOST" in result.overrides
    assert "APP_ENV" in result.overrides


def test_overrides_dict_excludes_non_overridden_key():
    result = stack_envs([BASE, OVERRIDE], ["base", "override"])
    assert "DB_PORT" not in result.overrides


def test_override_layer_names_recorded():
    result = stack_envs([BASE, OVERRIDE], ["base", "override"])
    assert result.overrides["DB_HOST"] == ["base", "override"]


def test_default_layer_names_generated():
    result = stack_envs([BASE, OVERRIDE])
    assert result.layers == ["layer0", "layer1"]


def test_mismatched_names_raises_value_error():
    with pytest.raises(ValueError):
        stack_envs([BASE, OVERRIDE], ["only_one_name"])


def test_empty_layer_list_returns_empty_env():
    result = stack_envs([])
    assert result.env == {}
    assert result.total_keys == 0


def test_to_summary_contains_layer_count():
    result = stack_envs([BASE, OVERRIDE], ["base", "override"])
    summary = result.to_summary()
    assert "2" in summary


def test_to_summary_contains_override_count():
    result = stack_envs([BASE, OVERRIDE], ["base", "override"])
    summary = result.to_summary()
    assert "Override" in summary
