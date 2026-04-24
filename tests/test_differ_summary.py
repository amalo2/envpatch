"""Tests for envpatch.differ_summary."""

import pytest

from envpatch.differ import DiffResult, EnvChange
from envpatch.differ_summary import DiffSummary, summarize_diff


def _make_change(key: str, old=None, new=None) -> EnvChange:
    return EnvChange(key=key, old_value=old, new_value=new)


def _make_diff(added=None, removed=None, modified=None, unchanged=None) -> DiffResult:
    return DiffResult(
        added=[_make_change(k, new="v") for k in (added or [])],
        removed=[_make_change(k, old="v") for k in (removed or [])],
        modified=[_make_change(k, old="a", new="b") for k in (modified or [])],
        unchanged=[_make_change(k, old="v", new="v") for k in (unchanged or [])],
    )


def test_summarize_diff_returns_diff_summary():
    diff = _make_diff(added=["A"])
    result = summarize_diff(diff)
    assert isinstance(result, DiffSummary)


def test_no_changes_has_no_changes_flag():
    diff = _make_diff()
    result = summarize_diff(diff)
    assert result.has_changes is False


def test_added_count_correct():
    diff = _make_diff(added=["A", "B"])
    result = summarize_diff(diff)
    assert result.added == 2


def test_removed_count_correct():
    diff = _make_diff(removed=["X"])
    result = summarize_diff(diff)
    assert result.removed == 1


def test_modified_count_correct():
    diff = _make_diff(modified=["M"])
    result = summarize_diff(diff)
    assert result.modified == 1


def test_unchanged_count_correct():
    diff = _make_diff(unchanged=["U", "V"])
    result = summarize_diff(diff)
    assert result.unchanged == 2


def test_total_changes_sums_add_remove_modify():
    diff = _make_diff(added=["A"], removed=["R"], modified=["M"])
    result = summarize_diff(diff)
    assert result.total_changes == 3


def test_severity_none_when_no_changes():
    diff = _make_diff()
    result = summarize_diff(diff)
    assert result.severity == "none"


def test_severity_low_for_single_addition():
    diff = _make_diff(added=["A"])
    result = summarize_diff(diff)
    assert result.severity == "low"


def test_severity_medium_for_modification():
    diff = _make_diff(modified=["M"])
    result = summarize_diff(diff)
    assert result.severity == "medium"


def test_severity_high_when_keys_removed():
    diff = _make_diff(removed=["R"])
    result = summarize_diff(diff)
    assert result.severity == "high"


def test_to_summary_no_changes_message():
    diff = _make_diff()
    result = summarize_diff(diff)
    assert result.to_summary() == "No changes detected."


def test_to_summary_contains_added_count():
    diff = _make_diff(added=["A", "B"])
    result = summarize_diff(diff)
    assert "+2 added" in result.to_summary()


def test_to_summary_contains_severity():
    diff = _make_diff(removed=["R"])
    result = summarize_diff(diff)
    assert "HIGH" in result.to_summary()


def test_to_dict_has_expected_keys():
    diff = _make_diff(added=["A"])
    result = summarize_diff(diff)
    d = result.to_dict()
    for key in ("added", "removed", "modified", "unchanged", "total_changes", "has_changes", "severity"):
        assert key in d


def test_to_dict_values_match_fields():
    diff = _make_diff(added=["A"], modified=["M"])
    result = summarize_diff(diff)
    d = result.to_dict()
    assert d["added"] == 1
    assert d["modified"] == 1
    assert d["total_changes"] == 2
