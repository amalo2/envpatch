import pytest
from click.testing import CliRunner
from envpatch.cli_freeze import freeze_cmd
import os


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nSECRET=abc\nDEBUG=true\n")
    return str(p)


def test_freeze_exits_zero(runner, env_file):
    result = runner.invoke(freeze_cmd, [env_file])
    assert result.exit_code == 0


def test_freeze_output_contains_marker(runner, env_file):
    result = runner.invoke(freeze_cmd, [env_file])
    assert "# frozen" in result.output


def test_freeze_specific_key(runner, env_file):
    result = runner.invoke(freeze_cmd, [env_file, "--key", "DB_HOST"])
    assert "DB_HOST=localhost  # frozen" in result.output


def test_freeze_specific_key_others_unchanged(runner, env_file):
    result = runner.invoke(freeze_cmd, [env_file, "--key", "DB_HOST"])
    assert "SECRET=abc" in result.output
    assert "SECRET=abc  # frozen" not in result.output


def test_freeze_custom_marker(runner, env_file):
    result = runner.invoke(freeze_cmd, [env_file, "--marker", "# locked"])
    assert "# locked" in result.output


def test_freeze_writes_to_output_file(runner, env_file, tmp_path):
    out = str(tmp_path / "out.env")
    result = runner.invoke(freeze_cmd, [env_file, "--output", out])
    assert result.exit_code == 0
    assert os.path.exists(out)
    with open(out) as f:
        content = f.read()
    assert "# frozen" in content


def test_freeze_summary_shown(runner, env_file):
    result = runner.invoke(freeze_cmd, [env_file])
    assert "Frozen:" in result.output or "Frozen:" in (result.stderr or "")
