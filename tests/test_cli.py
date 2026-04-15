"""Tests for the envpatch CLI commands."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from envpatch.cli import cli


BASE_ENV = """APP_NAME=myapp
DEBUG=false
SECRET_KEY=supersecret
"""

PATCH_ENV = """APP_NAME=myapp
DEBUG=true
NEW_FEATURE=enabled
"""


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_files(tmp_path):
    base = tmp_path / ".env.base"
    patch = tmp_path / ".env.patch"
    base.write_text(BASE_ENV)
    patch.write_text(PATCH_ENV)
    return base, patch


def test_diff_shows_added_keys(runner, env_files):
    base, patch = env_files
    result = runner.invoke(cli, ["diff", str(base), str(patch)])
    assert result.exit_code == 0
    assert "NEW_FEATURE" in result.output


def test_diff_shows_modified_keys(runner, env_files):
    base, patch = env_files
    result = runner.invoke(cli, ["diff", str(base), str(patch)])
    assert result.exit_code == 0
    assert "DEBUG" in result.output


def test_diff_shows_removed_keys(runner, env_files):
    base, patch = env_files
    result = runner.invoke(cli, ["diff", str(base), str(patch)])
    assert result.exit_code == 0
    assert "SECRET_KEY" in result.output


def test_diff_no_differences(runner, tmp_path):
    env = tmp_path / ".env"
    env.write_text(BASE_ENV)
    result = runner.invoke(cli, ["diff", str(env), str(env)])
    assert result.exit_code == 0
    assert "No differences found" in result.output


def test_apply_dry_run_does_not_write(runner, env_files):
    base, patch = env_files
    original_content = base.read_text()
    result = runner.invoke(cli, ["apply", str(base), str(patch), "--dry-run"])
    assert result.exit_code == 0
    assert base.read_text() == original_content


def test_apply_dry_run_shows_output(runner, env_files):
    base, patch = env_files
    result = runner.invoke(cli, ["apply", str(base), str(patch), "--dry-run"])
    assert result.exit_code == 0
    assert "NEW_FEATURE" in result.output
    assert "SECRET_KEY" in result.output


def test_apply_writes_to_output_file(runner, env_files, tmp_path):
    base, patch = env_files
    out = tmp_path / ".env.out"
    result = runner.invoke(cli, ["apply", str(base), str(patch), "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    content = out.read_text()
    assert "NEW_FEATURE" in content


def test_apply_preserves_existing_keys(runner, env_files, tmp_path):
    base, patch = env_files
    out = tmp_path / ".env.out"
    runner.invoke(cli, ["apply", str(base), str(patch), "--output", str(out)])
    content = out.read_text()
    assert "SECRET_KEY" in content
