"""Tests for envpatch.snapshot module."""

import json
from pathlib import Path

import pytest

from envpatch.snapshot import Snapshot, capture_snapshot, restore_snapshot


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("APP_NAME=myapp\nDEBUG=true\nSECRET=abc123\n", encoding="utf-8")
    return str(p)


@pytest.fixture
def snapshot_file(tmp_path):
    return str(tmp_path / "snapshot.json")


def test_capture_returns_snapshot(env_file):
    snap = capture_snapshot(env_file)
    assert isinstance(snap, Snapshot)


def test_capture_includes_all_keys(env_file):
    snap = capture_snapshot(env_file)
    assert snap.data["APP_NAME"] == "myapp"
    assert snap.data["DEBUG"] == "true"
    assert snap.data["SECRET"] == "abc123"


def test_capture_records_source_path(env_file):
    snap = capture_snapshot(env_file)
    assert snap.source_path == env_file


def test_capture_records_timestamp(env_file):
    snap = capture_snapshot(env_file)
    assert snap.captured_at is not None
    assert "T" in snap.captured_at  # ISO 8601


def test_capture_saves_snapshot_file(env_file, snapshot_file):
    capture_snapshot(env_file, snapshot_path=snapshot_file)
    assert Path(snapshot_file).exists()


def test_saved_snapshot_is_valid_json(env_file, snapshot_file):
    capture_snapshot(env_file, snapshot_path=snapshot_file)
    raw = json.loads(Path(snapshot_file).read_text(encoding="utf-8"))
    assert "data" in raw
    assert "source_path" in raw
    assert "captured_at" in raw


def test_snapshot_round_trip(env_file, snapshot_file):
    original = capture_snapshot(env_file, snapshot_path=snapshot_file)
    loaded = Snapshot.load(snapshot_file)
    assert loaded.data == original.data
    assert loaded.source_path == original.source_path
    assert loaded.captured_at == original.captured_at


def test_restore_writes_env_file(env_file, tmp_path):
    snap = capture_snapshot(env_file)
    target = str(tmp_path / "restored.env")
    restore_snapshot(snap, target_path=target)
    assert Path(target).exists()


def test_restore_contains_expected_keys(env_file, tmp_path):
    snap = capture_snapshot(env_file)
    target = str(tmp_path / "restored.env")
    restore_snapshot(snap, target_path=target)
    content = Path(target).read_text(encoding="utf-8")
    assert "APP_NAME=myapp" in content
    assert "DEBUG=true" in content


def test_snapshot_from_dict_roundtrip():
    raw = {"source_path": ".env", "captured_at": "2024-01-01T00:00:00+00:00", "data": {"X": "1"}}
    snap = Snapshot.from_dict(raw)
    assert snap.to_dict() == raw
