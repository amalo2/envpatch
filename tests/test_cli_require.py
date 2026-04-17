"""CLI tests for the require command."""
import pytest
from click.testing import CliRunner
from envpatch.cli_require import require_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET=xyz\n")
    return str(p)


def test_require_exits_zero_when_all_present(runner, env_file):
    result = runner.invoke(require_cmd, [env_file, "-k", "DB_HOST", "-k", "DB_PORT"])
    assert result.exit_code == 0


def test_require_shows_summary(runner, env_file):
    result = runner.invoke(require_cmd, [env_file, "-k", "DB_HOST"])
    assert "Required" in result.output


def test_require_shows_present_count(runner, env_file):
    result = runner.invoke(require_cmd, [env_file, "-k", "DB_HOST", "-k", "DB_PORT"])
    assert "Present" in result.output


def test_require_shows_missing_key(runner, env_file):
    result = runner.invoke(require_cmd, [env_file, "-k", "MISSING_KEY"])
    assert "MISSING_KEY" in result.output


def test_strict_exits_nonzero_on_missing(runner, env_file):
    result = runner.invoke(require_cmd, [env_file, "-k", "NO_SUCH_KEY", "--strict"])
    assert result.exit_code != 0


def test_strict_exits_zero_when_satisfied(runner, env_file):
    result = runner.invoke(require_cmd, [env_file, "-k", "DB_HOST", "--strict"])
    assert result.exit_code == 0


def test_no_strict_exits_zero_even_on_missing(runner, env_file):
    result = runner.invoke(require_cmd, [env_file, "-k", "GHOST"])
    assert result.exit_code == 0
