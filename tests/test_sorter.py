"""Tests for envpatch.sorter."""
import pytest
from envpatch.sorter import sort_env, SortResult


def test_sort_returns_sort_result():
    result = sort_env({"B": "1", "A": "2"})
    assert isinstance(result, SortResult)


def test_alphabetical_sort_order():
    result = sort_env({"ZEBRA": "1", "APPLE": "2", "MANGO": "3"})
    assert result.sorted_order == ["APPLE", "MANGO", "ZEBRA"]


def test_sorted_env_keys_match_sorted_order():
    result = sort_env({"C": "3", "A": "1", "B": "2"})
    assert list(result.sorted_env.keys()) == result.sorted_order


def test_values_preserved_after_sort():
    env = {"Z": "last", "A": "first"}
    result = sort_env(env)
    assert result.sorted_env["A"] == "first"
    assert result.sorted_env["Z"] == "last"


def test_original_order_preserved():
    env = {"B": "1", "A": "2", "C": "3"}
    result = sort_env(env)
    assert result.original_order == ["B", "A", "C"]


def test_changed_is_true_when_order_differs():
    result = sort_env({"B": "1", "A": "2"})
    assert result.changed is True


def test_changed_is_false_when_already_sorted():
    result = sort_env({"A": "1", "B": "2", "C": "3"})
    assert result.changed is False


def test_groups_applied_false_without_groups():
    result = sort_env({"B": "1", "A": "2"})
    assert result.groups_applied is False


def test_group_order_respected():
    env = {"DEBUG": "1", "APP_NAME": "app", "DB_HOST": "localhost"}
    groups = [["APP_NAME"], ["DB_HOST"]]
    result = sort_env(env, groups=groups)
    assert result.sorted_order[0] == "APP_NAME"
    assert result.sorted_order[1] == "DB_HOST"
    assert result.sorted_order[2] == "DEBUG"


def test_groups_applied_true_with_groups():
    result = sort_env({"B": "1", "A": "2"}, groups=[["B"]])
    assert result.groups_applied is True


def test_ungrouped_keys_sorted_alphabetically_after_groups():
    env = {"Z": "1", "A": "2", "PRIORITY": "3"}
    result = sort_env(env, groups=[["PRIORITY"]])
    assert result.sorted_order == ["PRIORITY", "A", "Z"]


def test_to_summary_already_sorted():
    result = sort_env({"A": "1", "B": "2"})
    assert "already" in result.to_summary()


def test_to_summary_alphabetical():
    result = sort_env({"B": "1", "A": "2"})
    summary = result.to_summary()
    assert "2" in summary
    assert "group" not in summary


def test_to_summary_with_groups():
    result = sort_env({"B": "1", "A": "2"}, groups=[["B"]])
    assert "group" in result.to_summary()
