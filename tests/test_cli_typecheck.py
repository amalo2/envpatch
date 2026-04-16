import pytest
from click.testing import CliRunner
from envpatch.cli_typecheck import typecheck_cmd
import tempfile, os


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("PORT=8080\nDEBUG=true\nAPP_NAME=myapp\n")
    return str(p)


def test_typecheck_exits_zero(runner, env_file):
    result = runner.invoke(typecheck_cmd, [env_file])
    assert result.exit_code == 0


def test_typecheck_shows_typed_count(runner, env_file):
    result = runner.invoke(typecheck_cmd, [env_file])
    assert "Typed keys" in result.output


def test_typecheck_shows_untyped_count(runner, env_file):
    result = runner.invoke(typecheck_cmd, [env_file])
    assert "Untyped keys" in result.output


def test_typecheck_shows_detected_type(runner, env_file):
    result = runner.invoke(typecheck_cmd, [env_file])
    assert "int" in result.output or "bool" in result.output


def test_show_untyped_flag_lists_keys(runner, env_file):
    result = runner.invoke(typecheck_cmd, [env_file, "--show-untyped"])
    assert "APP_NAME" in result.output


def test_fail_on_untyped_exits_one(runner, env_file):
    result = runner.invoke(typecheck_cmd, [env_file, "--fail-on-untyped"])
    assert result.exit_code == 1


def test_fully_typed_env_passes_fail_on_untyped(runner, tmp_path):
    p = tmp_path / ".env"
    p.write_text("PORT=8080\nDEBUG=true\n")
    result = runner.invoke(typecheck_cmd, [str(p), "--fail-on-untyped"])
    assert result.exit_code == 0
