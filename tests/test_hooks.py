"""Tests for envpatch.hooks audit integration."""
import json
import os
import pytest

from envpatch.differ import DiffResult, EnvChange
from envpatch.merger import MergeResult
from envpatch.hooks import audit_diff, audit_merge, audit_snapshot, ENV_AUDIT_LOG
from envpatch.auditor import load_log


@pytest.fixture(autouse=True)
def clear_audit_env():
    os.environ.pop(ENV_AUDIT_LOG, None)
    yield
    os.environ.pop(ENV_AUDIT_LOG, None)


@pytest.fixture
def log_path(tmp_path):
    path = str(tmp_path / "audit.json")
    os.environ[ENV_AUDIT_LOG] = path
    return path


def _make_diff() -> DiffResult:
    change = EnvChange(key="MOD", old_value="a", new_value="b")
    return DiffResult(
        changes={"ADD": EnvChange("ADD", None, "x"), "MOD": change},
        old_keys={"MOD"},
        new_keys={"ADD", "MOD"},
    )


def _make_merge() -> MergeResult:
    return MergeResult(
        env={"A": "1", "B": "2"},
        applied=["A"],
        skipped=["B"],
    )


def test_audit_diff_returns_none_when_no_log_configured():
    result = audit_diff(_make_diff())
    assert result is None


def test_audit_diff_writes_entry(log_path):
    audit_diff(_make_diff(), source="old.env", target="new.env")
    entries = load_log(log_path)
    assert len(entries) == 1
    assert entries[0].operation == "diff"


def test_audit_diff_records_added_keys(log_path):
    audit_diff(_make_diff())
    entries = load_log(log_path)
    assert "ADD" in entries[0].keys_added


def test_audit_diff_records_modified_keys(log_path):
    audit_diff(_make_diff())
    entries = load_log(log_path)
    assert "MOD" in entries[0].keys_modified


def test_audit_diff_records_source_and_target(log_path):
    audit_diff(_make_diff(), source="old.env", target="new.env")
    entries = load_log(log_path)
    assert entries[0].source == "old.env"
    assert entries[0].target == "new.env"


def test_audit_merge_returns_none_when_no_log_configured():
    result = audit_merge(_make_merge())
    assert result is None


def test_audit_merge_writes_entry(log_path):
    audit_merge(_make_merge(), source="patch.env", target="base.env")
    entries = load_log(log_path)
    assert entries[0].operation == "merge"


def test_audit_merge_records_applied_and_skipped(log_path):
    audit_merge(_make_merge())
    entries = load_log(log_path)
    assert entries[0].keys_added == ["A"]
    assert entries[0].keys_skipped == ["B"]


def test_audit_merge_records_source_and_target(log_path):
    audit_merge(_make_merge(), source="patch.env", target="base.env")
    entries = load_log(log_path)
    assert entries[0].source == "patch.env"
    assert entries[0].target == "base.env"


def test_audit_snapshot_returns_none_when_no_log_configured():
    result = audit_snapshot(["KEY1", "KEY2"])
    assert result is None


def test_audit_snapshot_writes_entry(log_path):
    audit_snapshot(["KEY1", "KEY2"], source="prod.env")
    entries = load_log(log_path)
    assert entries[0].operation == "snapshot"
    assert "KEY1" in entries[0].keys_added


def test_multiple_operations_accumulate_in_log(log_path):
    audit_diff(_make_diff())
    audit_merge(_make_merge())
    audit_snapshot(["X"])
    entries = load_log(log_path)
    assert len(entries) == 3
    assert [e.operation for e in entries] == ["diff", "merge", "snapshot"]
