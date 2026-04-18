import pytest
from click.testing import CliRunner
from envpatch.cli_pin import pin_cmd
import os


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nAPP_ENV=production\nAPI_KEY=abc123\n")
    return str(p)


def test_pin_exits_zero(runner, env_file):
    result = runner.invoke(pin_cmd, [env_file, "DB_HOST"])
    assert result.exit_code == 0


def test_pin_output_contains_marker(runner, env_file):
    result = runner.invoke(pin_cmd, [env_file, "DB_HOST"])
    assert "# pinned" in result.output


def test_pin_summary_shown(runner, env_file):
    result = runner.invoke(pin_cmd, [env_file, "DB_HOST"])
    assert "Pinned" in result.output


def test_pin_summary_only_flag(runner, env_file):
    result = runner.invoke(pin_cmd, [env_file, "DB_HOST", "--summary"])
    assert "Pinned" in result.output
    assert "DB_HOST=" not in result.output


def test_pin_write_updates_file(runner, env_file):
    runner.invoke(pin_cmd, [env_file, "DB_HOST", "--write"])
    content = open(env_file).read()
    assert "# pinned" in content


def test_pin_custom_marker(runner, env_file):
    result = runner.invoke(pin_cmd, [env_file, "API_KEY", "--marker", "# locked"])
    assert "# locked" in result.output


def test_pin_multiple_keys(runner, env_file):
    result = runner.invoke(pin_cmd, [env_file, "DB_HOST", "API_KEY"])
    lines = [l for l in result.output.splitlines() if "# pinned" in l]
    assert len(lines) == 2
