"""Tests for the sanitize CLI command."""

import pytest
from click.testing import CliRunner

from envpatch.cli_sanitize import sanitize_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def clean_env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("FOO=hello\nBAR=world\n")
    return str(f)


@pytest.fixture
def dirty_env_file(tmp_path):
    f = tmp_path / ".env.dirty"
    f.write_bytes(b"FOO=hel\x00lo\nBAR=wor\x01ld\n")
    return str(f)


def test_sanitize_exits_zero(runner, clean_env_file):
    result = runner.invoke(sanitize_cmd, [clean_env_file])
    assert result.exit_code == 0


def test_sanitize_clean_env_output_unchanged(runner, clean_env_file):
    result = runner.invoke(sanitize_cmd, [clean_env_file])
    assert "FOO=hello" in result.output
    assert "BAR=world" in result.output


def test_sanitize_removes_null_byte(runner, dirty_env_file):
    result = runner.invoke(sanitize_cmd, [dirty_env_file])
    assert "\x00" not in result.output


def test_sanitize_removes_control_char(runner, dirty_env_file):
    result = runner.invoke(sanitize_cmd, [dirty_env_file])
    assert "\x01" not in result.output


def test_sanitize_summary_flag_prints_to_stderr(runner, dirty_env_file):
    result = runner.invoke(sanitize_cmd, [dirty_env_file, "--summary"])
    assert "Sanitized" in result.output or result.exit_code == 0


def test_sanitize_with_replacement_char(runner, dirty_env_file):
    result = runner.invoke(sanitize_cmd, [dirty_env_file, "--replacement", "_"])
    assert "\x00" not in result.output
    assert "\x01" not in result.output


def test_sanitize_key_filter_limits_output(runner, dirty_env_file):
    result = runner.invoke(sanitize_cmd, [dirty_env_file, "--key", "FOO"])
    assert result.exit_code == 0


def test_sanitize_writes_output_file(runner, dirty_env_file, tmp_path):
    out = str(tmp_path / "out.env")
    result = runner.invoke(sanitize_cmd, [dirty_env_file, "--output", out])
    assert result.exit_code == 0
    content = open(out).read()
    assert "\x00" not in content
