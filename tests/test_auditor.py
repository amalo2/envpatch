"""Tests for envpatch.auditor module."""
import json
import os
import pytest
from pathlib import Path

from envpatch.auditor import (
    AuditEntry,
    make_entry,
    append_to_log,
    load_log,
)


@pytest.fixture
def log_file(tmp_path):
    return str(tmp_path / "audit.json")


def test_make_entry_returns_audit_entry():
    entry = make_entry("diff", source="old.env", target="new.env")
    assert isinstance(entry, AuditEntry)


def test_make_entry_sets_operation():
    entry = make_entry("apply")
    assert entry.operation == "apply"


def test_make_entry_sets_timestamp():
    entry = make_entry("merge")
    assert entry.timestamp is not None
    assert "T" in entry.timestamp  # ISO format


def test_make_entry_stores_source_and_target():
    entry = make_entry("diff", source="a.env", target="b.env")
    assert entry.source == "a.env"
    assert entry.target == "b.env"


def test_make_entry_stores_key_lists():
    entry = make_entry(
        "apply",
        keys_added=["NEW_KEY"],
        keys_modified=["CHANGED"],
        keys_skipped=["OLD"],
    )
    assert entry.keys_added == ["NEW_KEY"]
    assert entry.keys_modified == ["CHANGED"]
    assert entry.keys_skipped == ["OLD"]


def test_to_dict_contains_expected_keys():
    entry = make_entry("diff")
    d = entry.to_dict()
    assert "operation" in d
    assert "timestamp" in d
    assert "keys_added" in d


def test_from_dict_roundtrip():
    entry = make_entry("snapshot", source="env.file", keys_added=["A", "B"])
    restored = AuditEntry.from_dict(entry.to_dict())
    assert restored.operation == entry.operation
    assert restored.source == entry.source
    assert restored.keys_added == entry.keys_added


def test_append_to_log_creates_file(log_file):
    entry = make_entry("diff")
    append_to_log(entry, log_file)
    assert Path(log_file).exists()


def test_append_to_log_writes_valid_json(log_file):
    entry = make_entry("apply", keys_added=["X"])
    append_to_log(entry, log_file)
    with open(log_file) as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert data[0]["operation"] == "apply"


def test_append_to_log_accumulates_entries(log_file):
    append_to_log(make_entry("diff"), log_file)
    append_to_log(make_entry("apply"), log_file)
    entries = load_log(log_file)
    assert len(entries) == 2


def test_load_log_returns_empty_list_when_file_missing(tmp_path):
    result = load_log(str(tmp_path / "nonexistent.json"))
    assert result == []


def test_load_log_returns_audit_entries(log_file):
    append_to_log(make_entry("merge", keys_skipped=["SKIP"]), log_file)
    entries = load_log(log_file)
    assert isinstance(entries[0], AuditEntry)
    assert entries[0].keys_skipped == ["SKIP"]
