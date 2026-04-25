"""Tests for envpatch.archiver."""

import json
import zipfile
from pathlib import Path

import pytest

from envpatch.archiver import ArchiveResult, archive_envs


@pytest.fixture()
def env_files(tmp_path):
    f1 = tmp_path / ".env.base"
    f1.write_text("APP_ENV=production\nDEBUG=false\n")
    f2 = tmp_path / ".env.secrets"
    f2.write_text("SECRET_KEY=abc123\nDB_PASSWORD=hunter2\n")
    return [str(f1), str(f2)]


def test_archive_returns_archive_result(env_files, tmp_path):
    result = archive_envs(env_files, output_dir=str(tmp_path))
    assert isinstance(result, ArchiveResult)


def test_archive_file_is_created(env_files, tmp_path):
    result = archive_envs(env_files, output_dir=str(tmp_path))
    assert Path(result.archive_path).exists()


def test_archived_count_matches_files(env_files, tmp_path):
    result = archive_envs(env_files, output_dir=str(tmp_path))
    assert result.archived_count == 2


def test_skipped_count_zero_for_valid_files(env_files, tmp_path):
    result = archive_envs(env_files, output_dir=str(tmp_path))
    assert result.skipped_count == 0


def test_missing_file_is_skipped(tmp_path):
    result = archive_envs(["/nonexistent/.env"], output_dir=str(tmp_path))
    assert result.skipped_count == 1
    assert result.archived_count == 0


def test_archive_contains_env_files(env_files, tmp_path):
    result = archive_envs(env_files, output_dir=str(tmp_path))
    with zipfile.ZipFile(result.archive_path) as zf:
        names = zf.namelist()
    assert ".env.base" in names
    assert ".env.secrets" in names


def test_metadata_file_included_by_default(env_files, tmp_path):
    result = archive_envs(env_files, output_dir=str(tmp_path))
    with zipfile.ZipFile(result.archive_path) as zf:
        assert "_meta.json" in zf.namelist()


def test_metadata_excluded_when_flag_false(env_files, tmp_path):
    result = archive_envs(env_files, output_dir=str(tmp_path), include_metadata=False)
    with zipfile.ZipFile(result.archive_path) as zf:
        assert "_meta.json" not in zf.namelist()


def test_metadata_contains_file_list(env_files, tmp_path):
    result = archive_envs(env_files, output_dir=str(tmp_path))
    with zipfile.ZipFile(result.archive_path) as zf:
        meta = json.loads(zf.read("_meta.json"))
    assert ".env.base" in meta["files"]
    assert ".env.secrets" in meta["files"]


def test_label_appears_in_archive_name(env_files, tmp_path):
    result = archive_envs(env_files, output_dir=str(tmp_path), label="staging")
    assert "staging" in Path(result.archive_path).name


def test_created_at_is_set(env_files, tmp_path):
    result = archive_envs(env_files, output_dir=str(tmp_path))
    assert result.created_at != ""


def test_to_summary_contains_archive_path(env_files, tmp_path):
    result = archive_envs(env_files, output_dir=str(tmp_path))
    summary = result.to_summary()
    assert result.archive_path in summary


def test_to_summary_contains_archived_count(env_files, tmp_path):
    result = archive_envs(env_files, output_dir=str(tmp_path))
    assert "2" in result.to_summary()
