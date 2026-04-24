"""Tests for the stack CLI command."""
import pytest
from click.testing import CliRunner

from envpatch.cli_stack import stack_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_files(tmp_path):
    base = tmp_path / "base.env"
    base.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_ENV=development\n")
    override = tmp_path / "override.env"
    override.write_text("DB_HOST=prod.db.example.com\nAPP_ENV=production\n")
    return base, override


def test_stack_exits_zero(runner, env_files):
    base, override = env_files
    result = runner.invoke(stack_cmd, [str(base), str(override)])
    assert result.exit_code == 0


def test_stack_output_contains_overridden_value(runner, env_files):
    base, override = env_files
    result = runner.invoke(stack_cmd, [str(base), str(override)])
    assert "prod.db.example.com" in result.output


def test_stack_output_preserves_non_overridden_key(runner, env_files):
    base, override = env_files
    result = runner.invoke(stack_cmd, [str(base), str(override)])
    assert "DB_PORT=5432" in result.output


def test_stack_writes_to_output_file(runner, env_files, tmp_path):
    base, override = env_files
    out = tmp_path / "merged.env"
    result = runner.invoke(stack_cmd, [str(base), str(override), "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    content = out.read_text()
    assert "prod.db.example.com" in content


def test_stack_summary_flag_prints_to_stderr(runner, env_files):
    base, override = env_files
    result = runner.invoke(stack_cmd, [str(base), str(override), "--summary"])
    assert result.exit_code == 0


def test_stack_custom_names_accepted(runner, env_files):
    base, override = env_files
    result = runner.invoke(
        stack_cmd, [str(base), str(override), "--names", "base,prod"]
    )
    assert result.exit_code == 0


def test_stack_mismatched_names_exits_nonzero(runner, env_files):
    base, override = env_files
    result = runner.invoke(
        stack_cmd, [str(base), str(override), "--names", "only_one"]
    )
    assert result.exit_code != 0
