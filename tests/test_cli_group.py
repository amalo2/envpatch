import pytest
from click.testing import CliRunner
from envpatch.cli_group import group_cmd
import tempfile, os


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nAWS_KEY=abc\nPORT=8080\n")
    return str(p)


def test_group_exits_zero(runner, env_file):
    result = runner.invoke(group_cmd, [env_file])
    assert result.exit_code == 0


def test_summary_contains_group_name(runner, env_file):
    result = runner.invoke(group_cmd, [env_file])
    assert "DB" in result.output


def test_summary_contains_aws_group(runner, env_file):
    result = runner.invoke(group_cmd, [env_file])
    assert "AWS" in result.output


def test_list_mode_shows_keys(runner, env_file):
    result = runner.invoke(group_cmd, [env_file, "--list"])
    assert "DB_HOST" in result.output
    assert "AWS_KEY" in result.output


def test_list_mode_shows_ungrouped(runner, env_file):
    result = runner.invoke(group_cmd, [env_file, "--list"])
    assert "ungrouped" in result.output
    assert "PORT" in result.output


def test_prefix_filter_shows_only_group(runner, env_file):
    result = runner.invoke(group_cmd, [env_file, "--prefix", "DB"])
    assert "DB_HOST" in result.output
    assert "AWS_KEY" not in result.output


def test_prefix_filter_missing_exits_nonzero(runner, env_file):
    result = runner.invoke(group_cmd, [env_file, "--prefix", "MISSING"])
    assert result.exit_code != 0


def test_custom_delimiter(runner, tmp_path):
    p = tmp_path / ".env"
    p.write_text("APP.NAME=foo\nAPP.ENV=prod\nPORT=80\n")
    result = runner.invoke(group_cmd, [str(p), "--delimiter", "."])
    assert "APP" in result.output
