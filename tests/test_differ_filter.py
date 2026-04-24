"""Tests for envpatch.differ_filter."""
import pytest

from envpatch.differ import DiffResult, EnvChange
from envpatch.differ_filter import FilterResult, filter_diff


def _make_diff(*changes: EnvChange, unchanged=()) -> DiffResult:
    dr = DiffResult()
    for c in changes:
        dr.changes.append(c)
    for u in unchanged:
        dr.unchanged.append(u)
    return dr


def _change(key: str, change_type: str, old=None, new=None) -> EnvChange:
    return EnvChange(key=key, change_type=change_type, old_value=old, new_value=new)


# --- return type ---

def test_filter_returns_filter_result():
    diff = _make_diff()
    result = filter_diff(diff)
    assert isinstance(result, FilterResult)


def test_no_filters_returns_all_changes():
    diff = _make_diff(
        _change("A", "added"),
        _change("B", "removed"),
    )
    result = filter_diff(diff)
    assert result.matched_count == 2
    assert result.excluded_count == 0


# --- change_type filter ---

def test_type_filter_keeps_only_added():
    diff = _make_diff(
        _change("A", "added"),
        _change("B", "removed"),
        _change("C", "modified", old="x", new="y"),
    )
    result = filter_diff(diff, change_types=["added"])
    assert all(c.change_type == "added" for c in result.matched)
    assert result.matched_count == 1


def test_type_filter_multiple_types():
    diff = _make_diff(
        _change("A", "added"),
        _change("B", "removed"),
        _change("C", "modified", old="x", new="y"),
    )
    result = filter_diff(diff, change_types=["added", "removed"])
    assert result.matched_count == 2


# --- pattern filter ---

def test_pattern_filter_matches_prefix():
    diff = _make_diff(
        _change("DB_HOST", "added"),
        _change("DB_PORT", "added"),
        _change("AWS_KEY", "added"),
    )
    result = filter_diff(diff, pattern=r"^DB_")
    assert result.matched_count == 2
    assert all(c.key.startswith("DB_") for c in result.matched)


def test_pattern_filter_no_match_goes_to_excluded():
    diff = _make_diff(_change("FOO", "added"))
    result = filter_diff(diff, pattern=r"^DB_")
    assert result.matched_count == 0
    assert result.excluded_count == 1


# --- combined filters ---

def test_pattern_and_type_combined():
    diff = _make_diff(
        _change("DB_HOST", "added"),
        _change("DB_PORT", "removed"),
        _change("AWS_KEY", "added"),
    )
    result = filter_diff(diff, pattern=r"^DB_", change_types=["added"])
    assert result.matched_count == 1
    assert result.matched[0].key == "DB_HOST"


# --- include_unchanged ---

def test_unchanged_excluded_by_default():
    diff = _make_diff(unchanged=[_change("STATIC", "unchanged")])
    result = filter_diff(diff)
    assert result.matched_count == 0


def test_include_unchanged_adds_them():
    diff = _make_diff(unchanged=[_change("STATIC", "unchanged")])
    result = filter_diff(diff, include_unchanged=True)
    assert result.matched_count == 1


# --- metadata ---

def test_filter_pattern_stored_in_result():
    diff = _make_diff()
    result = filter_diff(diff, pattern=r"^DB_")
    assert result.filter_pattern == r"^DB_"


def test_change_types_stored_in_result():
    diff = _make_diff()
    result = filter_diff(diff, change_types=["added"])
    assert result.change_types == ["added"]


def test_to_summary_contains_counts():
    diff = _make_diff(_change("A", "added"))
    result = filter_diff(diff)
    summary = result.to_summary()
    assert "matched=" in summary
    assert "excluded=" in summary
