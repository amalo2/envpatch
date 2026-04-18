import pytest
from click.testing import CliRunner
from envpatch.cli_alias import alias_cmd
import os


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DATABASE_URL=postgres://localhost/db\nPORT=8080\n")
    return str(p)


def test_alias_exits_zero(runner, env_file):
    result = runner.invoke(alias_cmd, [env_file, "--map", "PORT:APP_PORT"])
    assert result.exit_code == 0


def test_alias_output_contains_alias_key(runner, env_file):
    result = runner.invoke(alias_cmd, [env_file, "--map", "PORT:APP_PORT"])
    assert "APP_PORT" in result.output


def test_alias_value_matches_source(runner, env_file):
    result = runner.invoke(alias_cmd, [env_file, "--map", "PORT:APP_PORT"])
    assert "APP_PORT=8080" in result.output


def test_alias_source_key_preserved(runner, env_file):
    result = runner.invoke(alias_cmd, [env_file, "--map", "PORT:APP_PORT"])
    assert "PORT=8080" in result.output


def test_alias_summary_flag(runner, env_file):
    result = runner.invoke(alias_cmd, [env_file, "--map", "PORT:APP_PORT", "--summary"])
    assert result.exit_code == 0


def test_alias_invalid_map_format(runner, env_file):
    result = runner.invoke(alias_cmd, [env_file, "--map", "BADFORMAT"])
    assert result.exit_code != 0


def test_alias_output_to_file(runner, env_file, tmp_path):
    out = str(tmp_path / "out.env")
    result = runner.invoke(alias_cmd, [env_file, "--map", "PORT:APP_PORT", "--output", out])
    assert result.exit_code == 0
    assert os.path.exists(out)
    content = open(out).read()
    assert "APP_PORT=8080" in content
