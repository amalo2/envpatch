"""Tests for envpatch.comparator."""

import json
import pytest
from unittest.mock import patch, MagicMock
from envpatch.comparator import compare_snapshots, compare_snapshot_files, CompareResult
from envpatch.snapshot import Snapshot


def _make_snapshot(data: dict, path: str = ".env", ts: str = "2024-01-01T00:00:00") -> Snapshot:
    snap = MagicMock(spec=Snapshot)
    snap.data = data
    snap.source_path = path
    snap.captured_at = ts
    return snap


def test_compare_returns_compare_result():
    src = _make_snapshot({"A": "1"})
    tgt = _make_snapshot({"A": "1"})
    result = compare_snapshots(src, tgt)
    assert isinstance(result, CompareResult)


def test_no_changes_when_identical():
    src = _make_snapshot({"A": "1", "B": "2"})
    tgt = _make_snapshot({"A": "1", "B": "2"})
    result = compare_snapshots(src, tgt)
    assert not result.has_changes


def test_detects_added_keys():
    src = _make_snapshot({"A": "1"})
    tgt = _make_snapshot({"A": "1", "B": "2"})
    result = compare_snapshots(src, tgt)
    assert result.added_count == 1


def test_detects_removed_keys():
    src = _make_snapshot({"A": "1", "B": "2"})
    tgt = _make_snapshot({"A": "1"})
    result = compare_snapshots(src, tgt)
    assert result.removed_count == 1


def test_detects_modified_keys():
    src = _make_snapshot({"A": "old"})
    tgt = _make_snapshot({"A": "new"})
    result = compare_snapshots(src, tgt)
    assert result.modified_count == 1


def test_source_metadata_preserved():
    src = _make_snapshot({}, path="/tmp/src.snap", ts="2024-01-01T10:00:00")
    tgt = _make_snapshot({}, path="/tmp/tgt.snap", ts="2024-06-01T12:00:00")
    result = compare_snapshots(src, tgt)
    assert result.source_path == "/tmp/src.snap"
    assert result.source_timestamp == "2024-01-01T10:00:00"


def test_target_metadata_preserved():
    src = _make_snapshot({})
    tgt = _make_snapshot({}, path="/tmp/tgt.snap", ts="2024-06-01T12:00:00")
    result = compare_snapshots(src, tgt)
    assert result.target_path == "/tmp/tgt.snap"
    assert result.target_timestamp == "2024-06-01T12:00:00"


def test_to_summary_contains_counts():
    src = _make_snapshot({"A": "1"})
    tgt = _make_snapshot({"A": "changed", "B": "new"})
    result = compare_snapshots(src, tgt)
    summary = result.to_summary()
    assert "Added:" in summary
    assert "Removed:" in summary
    assert "Modified:" in summary


def test_to_summary_no_changes_message():
    src = _make_snapshot({"A": "1"})
    tgt = _make_snapshot({"A": "1"})
    result = compare_snapshots(src, tgt)
    assert "No differences found." in result.to_summary()


def test_compare_snapshot_files_loads_and_compares(tmp_path):
    from envpatch.snapshot import Snapshot

    data_a = {"KEY": "alpha"}
    data_b = {"KEY": "beta", "NEW": "value"}

    snap_a = Snapshot(data=data_a, source_path="a.env", captured_at="2024-01-01T00:00:00")
    snap_b = Snapshot(data=data_b, source_path="b.env", captured_at="2024-02-01T00:00:00")

    path_a = tmp_path / "a.snap"
    path_b = tmp_path / "b.snap"
    snap_a.save(str(path_a))
    snap_b.save(str(path_b))

    result = compare_snapshot_files(str(path_a), str(path_b))
    assert result.added_count == 1
    assert result.modified_count == 1
