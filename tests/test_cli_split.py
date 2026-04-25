"""Tests for the split CLI command."""
import os

import pytest
from click.testing import CliRunner

from envpatch.cli_split import split_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "DB_HOST=localhost\nDB_PORT=5432\nAWS_KEY=abc123\nPORT=8080\n"
    )
    return str(p)


def test_split_exits_zero(runner, env_file, tmp_path):
    result = runner.invoke(
        split_cmd,
        [env_file, "--prefix", "DB_", "--output-dir", str(tmp_path), "--dry-run"],
    )
    assert result.exit_code == 0


def test_split_summary_contains_prefix(runner, env_file, tmp_path):
    result = runner.invoke(
        split_cmd,
        [env_file, "--prefix", "DB_", "--output-dir", str(tmp_path), "--dry-run"],
    )
    assert "DB_" in result.output


def test_split_writes_segment_file(runner, env_file, tmp_path):
    runner.invoke(
        split_cmd,
        [env_file, "--prefix", "DB_", "--output-dir", str(tmp_path)],
    )
    out = tmp_path / "db.env"
    assert out.exists()


def test_split_segment_file_contains_key(runner, env_file, tmp_path):
    runner.invoke(
        split_cmd,
        [env_file, "--prefix", "DB_", "--output-dir", str(tmp_path)],
    )
    content = (tmp_path / "db.env").read_text()
    assert "DB_HOST" in content


def test_split_unmatched_file_written(runner, env_file, tmp_path):
    runner.invoke(
        split_cmd,
        [env_file, "--prefix", "DB_", "--output-dir", str(tmp_path)],
    )
    assert (tmp_path / "unmatched.env").exists()


def test_split_no_unmatched_flag_skips_file(runner, env_file, tmp_path):
    runner.invoke(
        split_cmd,
        [
            env_file,
            "--prefix", "DB_",
            "--output-dir", str(tmp_path),
            "--no-unmatched",
        ],
    )
    assert not (tmp_path / "unmatched.env").exists()


def test_dry_run_does_not_write_files(runner, env_file, tmp_path):
    runner.invoke(
        split_cmd,
        [
            env_file,
            "--prefix", "DB_",
            "--output-dir", str(tmp_path),
            "--dry-run",
        ],
    )
    assert not (tmp_path / "db.env").exists()


def test_split_missing_input_file_exits_nonzero(runner, tmp_path):
    """Invoking split with a non-existent input file should exit with a non-zero code."""
    result = runner.invoke(
        split_cmd,
        [
            str(tmp_path / "nonexistent.env"),
            "--prefix", "DB_",
            "--output-dir", str(tmp_path),
        ],
    )
    assert result.exit_code != 0
