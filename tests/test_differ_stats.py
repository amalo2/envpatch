"""Tests for envpatch.differ_stats."""
import pytest

from envpatch.differ import DiffResult, EnvChange
from envpatch.differ_stats import DiffStats, compute_stats


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #

def _change(key: str, change_type: str, old=None, new=None) -> EnvChange:
    return EnvChange(key=key, change_type=change_type, old_value=old, new_value=new)


def _make_diff(*changes: EnvChange) -> DiffResult:
    return DiffResult(changes=list(changes))


# ------------------------------------------------------------------ #
# Basic return type
# ------------------------------------------------------------------ #

def test_compute_stats_returns_diff_stats():
    diff = _make_diff()
    result = compute_stats(diff)
    assert isinstance(result, DiffStats)


def test_empty_diff_has_no_changes():
    diff = _make_diff()
    result = compute_stats(diff)
    assert not result.has_changes
    assert result.total_changes == 0


# ------------------------------------------------------------------ #
# Counts
# ------------------------------------------------------------------ #

def test_added_count_correct():
    diff = _make_diff(
        _change("NEW_KEY", "added", new="val"),
        _change("ANOTHER", "added", new="x"),
    )
    result = compute_stats(diff)
    assert result.added_count == 2


def test_removed_count_correct():
    diff = _make_diff(_change("OLD_KEY", "removed", old="gone"))
    result = compute_stats(diff)
    assert result.removed_count == 1


def test_modified_count_correct():
    diff = _make_diff(_change("DB_HOST", "modified", old="localhost", new="prod.db"))
    result = compute_stats(diff)
    assert result.modified_count == 1


def test_total_changes_is_sum_of_all_types():
    diff = _make_diff(
        _change("A", "added", new="1"),
        _change("B", "removed", old="2"),
        _change("C", "modified", old="3", new="4"),
    )
    result = compute_stats(diff)
    assert result.total_changes == 3


# ------------------------------------------------------------------ #
# Change ratio
# ------------------------------------------------------------------ #

def test_change_ratio_uses_provided_universe():
    diff = _make_diff(_change("A", "added", new="1"))
    result = compute_stats(diff, total_key_universe=10)
    assert result.change_ratio == pytest.approx(0.1)


def test_change_ratio_capped_at_one():
    diff = _make_diff(
        _change("A", "added", new="1"),
        _change("B", "added", new="2"),
    )
    result = compute_stats(diff, total_key_universe=1)
    assert result.change_ratio <= 1.0


# ------------------------------------------------------------------ #
# most_changed_keys ordering
# ------------------------------------------------------------------ #

def test_most_changed_keys_contains_all_changed_keys():
    diff = _make_diff(
        _change("A", "added", new="1"),
        _change("B", "modified", old="x", new="y"),
    )
    result = compute_stats(diff)
    assert "A" in result.most_changed_keys
    assert "B" in result.most_changed_keys


def test_modified_keys_appear_before_added_in_most_changed():
    diff = _make_diff(
        _change("ADDED_KEY", "added", new="1"),
        _change("MOD_KEY", "modified", old="a", new="b"),
    )
    result = compute_stats(diff)
    assert result.most_changed_keys.index("MOD_KEY") < result.most_changed_keys.index("ADDED_KEY")


# ------------------------------------------------------------------ #
# Breakdown dict
# ------------------------------------------------------------------ #

def test_change_type_breakdown_populated():
    diff = _make_diff(
        _change("A", "added", new="1"),
        _change("B", "added", new="2"),
        _change("C", "removed", old="3"),
    )
    result = compute_stats(diff)
    assert result.change_type_breakdown["added"] == 2
    assert result.change_type_breakdown["removed"] == 1


# ------------------------------------------------------------------ #
# Serialisation helpers
# ------------------------------------------------------------------ #

def test_to_dict_has_expected_keys():
    diff = _make_diff(_change("X", "added", new="v"))
    d = compute_stats(diff).to_dict()
    for key in ("total_changes", "added_count", "removed_count", "modified_count",
                "change_ratio", "most_changed_keys", "change_type_breakdown"):
        assert key in d


def test_to_summary_returns_string():
    diff = _make_diff(_change("X", "modified", old="a", new="b"))
    summary = compute_stats(diff).to_summary()
    assert isinstance(summary, str)
    assert "Modified" in summary
