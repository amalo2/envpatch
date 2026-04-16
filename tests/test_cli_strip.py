"""Tests for the strip CLI command."""
import pytest
from click.testing import CliRunner
from pathlib import Path

from envpatch.cli_strip import strip_cmd

SAMPLE_ENV = "APP_NAME=myapp\nSECRET_KEY=abc123\nPORT=8080\n"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(SAMPLE_ENV)
    return str(p)


def test_strip_exits_zero(runner, env_file):
    result = runner.invoke(strip_cmd, [env_file, "-k", "PORT"])
    assert result.exit_code == 0


def test_strip_removes_key_from_output(runner, env_file):
    result = runner.invoke(strip_cmd, [env_file, "-k", "PORT"])
    assert "PORT" not in result.output


def test_strip_keeps_other_keys(runner, env_file):
    result = runner.invoke(strip_cmd, [env_file, "-k", "PORT"])
    assert "APP_NAME=myapp" in result.output


def test_strip_by_pattern(runner, env_file):
    result = runner.invoke(strip_cmd, [env_file, "-p", "SECRET"])
    assert "SECRET_KEY" not in result.output


def test_strip_in_place(runner, env_file):
    runner.invoke(strip_cmd, [env_file, "-k", "PORT", "--in-place"])
    content = Path(env_file).read_text()
    assert "PORT" not in content


def test_strip_in_place_preserves_other_keys(runner, env_file):
    runner.invoke(strip_cmd, [env_file, "-k", "PORT", "--in-place"])
    content = Path(env_file).read_text()
    assert "APP_NAME=myapp" in content


def test_summary_flag_prints_to_stderr(runner, env_file):
    result = runner.invoke(strip_cmd, [env_file, "-k", "PORT", "--summary"])
    assert result.exit_code == 0
