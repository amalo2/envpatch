"""CLI tests for the inject command."""
import json

import pytest
from click.testing import CliRunner

from envpatch.cli_inject import inject_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_KEY=secret\n")
    return str(p)


def test_inject_exits_zero(runner, env_file):
    result = runner.invoke(inject_cmd, [env_file])
    assert result.exit_code == 0


def test_inject_text_contains_summary(runner, env_file):
    result = runner.invoke(inject_cmd, [env_file])
    assert "Injected" in result.output


def test_inject_text_shows_injected_keys(runner, env_file):
    result = runner.invoke(inject_cmd, [env_file])
    assert "DB_HOST" in result.output


def test_inject_json_is_parseable(runner, env_file):
    result = runner.invoke(inject_cmd, [env_file, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "injected" in data


def test_inject_json_injected_count(runner, env_file):
    result = runner.invoke(inject_cmd, [env_file, "--format", "json"])
    data = json.loads(result.output)
    assert data["injected_count"] == 3


def test_inject_export_format_contains_export(runner, env_file):
    result = runner.invoke(inject_cmd, [env_file, "--format", "export"])
    assert result.exit_code == 0
    assert "export DB_HOST" in result.output


def test_inject_prefix_applied(runner, env_file):
    result = runner.invoke(inject_cmd, [env_file, "--prefix", "TEST_", "--format", "json"])
    data = json.loads(result.output)
    assert any(k.startswith("TEST_") for k in data["injected"])
