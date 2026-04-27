"""Tests for envpatch.differ_merge."""
import pytest

from envpatch.differ import DiffResult, EnvChange
from envpatch.differ_merge import MergeDiffResult, merge_diffs


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _change(key: str, old: str | None, new: str | None) -> EnvChange:
    change_type = "added" if old is None else ("removed" if new is None else "modified")
    return EnvChange(key=key, change_type=change_type, old_value=old, new_value=new)


def _diff(*changes: EnvChange) -> DiffResult:
    dr = DiffResult()
    for c in changes:
        dr.changes.append(c)
    return dr


# ---------------------------------------------------------------------------
# return type
# ---------------------------------------------------------------------------

def test_merge_diffs_returns_merge_diff_result():
    result = merge_diffs(_diff(), _diff())
    assert isinstance(result, MergeDiffResult)


def test_empty_diffs_produce_empty_result():
    result = merge_diffs(_diff(), _diff())
    assert result.changes == []
    assert result.conflict_keys == []


# ---------------------------------------------------------------------------
# source_a_only / source_b_only
# ---------------------------------------------------------------------------

def test_key_only_in_a_goes_to_source_a_only():
    result = merge_diffs(_diff(_change("FOO", None, "bar")), _diff())
    assert "FOO" in result.source_a_only


def test_key_only_in_b_goes_to_source_b_only():
    result = merge_diffs(_diff(), _diff(_change("BAZ", None, "qux")))
    assert "BAZ" in result.source_b_only


def test_key_only_in_a_included_in_changes():
    result = merge_diffs(_diff(_change("FOO", None, "bar")), _diff())
    keys = [c.key for c in result.changes]
    assert "FOO" in keys


def test_key_only_in_b_included_in_changes():
    result = merge_diffs(_diff(), _diff(_change("BAR", "old", "new")))
    keys = [c.key for c in result.changes]
    assert "BAR" in keys


# ---------------------------------------------------------------------------
# conflict detection
# ---------------------------------------------------------------------------

def test_same_key_different_values_is_conflict():
    a = _diff(_change("KEY", "old", "val_a"))
    b = _diff(_change("KEY", "old", "val_b"))
    result = merge_diffs(a, b)
    assert "KEY" in result.conflict_keys


def test_same_key_same_value_is_not_conflict():
    a = _diff(_change("KEY", "old", "same"))
    b = _diff(_change("KEY", "old", "same"))
    result = merge_diffs(a, b)
    assert "KEY" not in result.conflict_keys


def test_has_conflicts_true_when_conflict_exists():
    a = _diff(_change("KEY", "old", "val_a"))
    b = _diff(_change("KEY", "old", "val_b"))
    result = merge_diffs(a, b)
    assert result.has_conflicts is True


def test_has_conflicts_false_when_no_conflicts():
    result = merge_diffs(_diff(_change("A", None, "1")), _diff(_change("B", None, "2")))
    assert result.has_conflicts is False


# ---------------------------------------------------------------------------
# prefer flag
# ---------------------------------------------------------------------------

def test_prefer_b_wins_on_conflict():
    a = _diff(_change("KEY", "old", "from_a"))
    b = _diff(_change("KEY", "old", "from_b"))
    result = merge_diffs(a, b, prefer="b")
    winning = next(c for c in result.changes if c.key == "KEY")
    assert winning.new_value == "from_b"


def test_prefer_a_wins_on_conflict():
    a = _diff(_change("KEY", "old", "from_a"))
    b = _diff(_change("KEY", "old", "from_b"))
    result = merge_diffs(a, b, prefer="a")
    winning = next(c for c in result.changes if c.key == "KEY")
    assert winning.new_value == "from_a"


def test_invalid_prefer_raises_value_error():
    with pytest.raises(ValueError):
        merge_diffs(_diff(), _diff(), prefer="c")


# ---------------------------------------------------------------------------
# to_summary
# ---------------------------------------------------------------------------

def test_to_summary_returns_string():
    result = merge_diffs(_diff(_change("X", None, "1")), _diff(_change("Y", None, "2")))
    assert isinstance(result.to_summary(), str)


def test_to_summary_contains_conflict_count():
    a = _diff(_change("K", "o", "v1"))
    b = _diff(_change("K", "o", "v2"))
    result = merge_diffs(a, b)
    assert "1" in result.to_summary()
