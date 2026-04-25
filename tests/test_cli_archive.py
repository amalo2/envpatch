"""CLI tests for the archive command."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from envpatch.cli_archive import archive_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_files(tmp_path):
    f1 = tmp_path / ".env.base"
    f1.write_text("APP=prod\n")
    f2 = tmp_path / ".env.extra"
    f2.write_text("EXTRA=yes\n")
    return tmp_path, [str(f1), str(f2)]


def test_archive_exits_zero(runner, env_files, tmp_path):
    base_dir, files = env_files
    result = runner.invoke(archive_cmd, files + ["--output-dir", str(tmp_path)])
    assert result.exit_code == 0


def test_archive_summary_shown(runner, env_files, tmp_path):
    base_dir, files = env_files
    result = runner.invoke(archive_cmd, files + ["--output-dir", str(tmp_path)])
    assert "Archive" in result.output


def test_archive_file_created(runner, env_files, tmp_path):
    base_dir, files = env_files
    runner.invoke(archive_cmd, files + ["--output-dir", str(tmp_path)])
    zips = list(tmp_path.glob("*.zip"))
    assert len(zips) == 1


def test_archive_label_in_filename(runner, env_files, tmp_path):
    base_dir, files = env_files
    runner.invoke(
        archive_cmd, files + ["--output-dir", str(tmp_path), "--label", "prod"]
    )
    zips = list(tmp_path.glob("*prod*.zip"))
    assert len(zips) == 1


def test_archive_quiet_suppresses_output(runner, env_files, tmp_path):
    base_dir, files = env_files
    result = runner.invoke(
        archive_cmd, files + ["--output-dir", str(tmp_path), "--quiet"]
    )
    assert result.output.strip() == ""


def test_archive_no_metadata_flag(runner, env_files, tmp_path):
    import zipfile

    base_dir, files = env_files
    runner.invoke(
        archive_cmd, files + ["--output-dir", str(tmp_path), "--no-metadata"]
    )
    zips = list(tmp_path.glob("*.zip"))
    assert zips
    with zipfile.ZipFile(zips[0]) as zf:
        assert "_meta.json" not in zf.namelist()
