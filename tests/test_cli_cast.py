import json
import pytest
from click.testing import CliRunner
from envpatch.cli_cast import cast_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("PORT=8080\nDEBUG=true\nNAME=myapp\nRATIO=1.5\n")
    return str(f)


def test_cast_exits_zero(runner, env_file):
    result = runner.invoke(cast_cmd, [env_file])
    assert result.exit_code == 0


def test_cast_text_contains_summary(runner, env_file):
    result = runner.invoke(cast_cmd, [env_file])
    assert "Cast" in result.output


def test_cast_text_shows_types(runner, env_file):
    result = runner.invoke(cast_cmd, [env_file])
    assert "int" in result.output or "bool" in result.output


def test_cast_json_is_parseable(runner, env_file):
    result = runner.invoke(cast_cmd, [env_file, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, dict)


def test_cast_json_int_value(runner, env_file):
    result = runner.invoke(cast_cmd, [env_file, "--format", "json"])
    data = json.loads(result.output)
    assert data["PORT"] == 8080


def test_cast_json_bool_value(runner, env_file):
    result = runner.invoke(cast_cmd, [env_file, "--format", "json"])
    data = json.loads(result.output)
    assert data["DEBUG"] is True


def test_cast_selective_keys(runner, env_file):
    result = runner.invoke(cast_cmd, [env_file, "-k", "PORT", "--format", "json"])
    data = json.loads(result.output)
    assert isinstance(data["PORT"], int)
    assert isinstance(data["NAME"], str)
