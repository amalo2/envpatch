"""Tests for envpatch.unpacker."""
from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from envpatch.unpacker import UnpackResult, unpack_env


@pytest.fixture()
def archive(tmp_path: Path) -> Path:
    """Build a small zip archive containing two .env files."""
    zip_path = tmp_path / "envs.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(".env.production", "APP_ENV=production\nSECRET=abc\n")
        zf.writestr(".env.staging", "APP_ENV=staging\nSECRET=xyz\n")
    return zip_path


def test_unpack_returns_unpack_result(archive: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    result = unpack_env(str(archive), dest_dir=str(out))
    assert isinstance(result, UnpackResult)


def test_extracted_count_matches_members(archive: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    result = unpack_env(str(archive), dest_dir=str(out))
    assert result.extracted_count == 2


def test_skipped_count_zero_on_fresh_extract(archive: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    result = unpack_env(str(archive), dest_dir=str(out))
    assert result.skipped_count == 0


def test_files_actually_created(archive: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    unpack_env(str(archive), dest_dir=str(out))
    assert (out / ".env.production").exists()
    assert (out / ".env.staging").exists()


def test_existing_file_skipped_by_default(archive: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    unpack_env(str(archive), dest_dir=str(out))
    # second call — files already exist
    result = unpack_env(str(archive), dest_dir=str(out))
    assert result.skipped_count == 2
    assert result.extracted_count == 0


def test_existing_file_overwritten_when_flag_set(archive: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    unpack_env(str(archive), dest_dir=str(out))
    result = unpack_env(str(archive), dest_dir=str(out), overwrite=True)
    assert result.extracted_count == 2
    assert result.skipped_count == 0


def test_pattern_filters_members(archive: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    result = unpack_env(str(archive), dest_dir=str(out), pattern="production")
    assert result.extracted_count == 1
    assert result.extracted[0] == ".env.production"


def test_destination_recorded_in_result(archive: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    result = unpack_env(str(archive), dest_dir=str(out))
    assert str(out.resolve()) == result.destination


def test_to_summary_contains_extracted_count(archive: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    result = unpack_env(str(archive), dest_dir=str(out))
    summary = result.to_summary()
    assert "Extracted" in summary
    assert "2" in summary


def test_to_summary_lists_file_names(archive: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    result = unpack_env(str(archive), dest_dir=str(out))
    summary = result.to_summary()
    assert ".env.production" in summary
    assert ".env.staging" in summary
