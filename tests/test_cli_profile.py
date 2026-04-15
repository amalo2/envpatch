"""Tests for the `profile` CLI sub-command."""
import json
import pytest
from click.testing import CliRunner

from envpatch.cli_profile import profile_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "APP_NAME=myapp\n"
        "APP_SECRET=topsecret\n"
        "DATABASE_PASSWORD=dbpass\n"
        "DEBUG=\n"
        "PORT=8080\n"
        "REPLICA_PORT=8080\n"
    )
    return str(p)


def test_profile_exits_zero(runner, env_file):
    result = runner.invoke(profile_cmd, [env_file])
    assert result.exit_code == 0


def test_profile_text_contains_total(runner, env_file):
    result = runner.invoke(profile_cmd, [env_file])
    assert "Total keys" in result.output
    assert "6" in result.output


def test_profile_text_contains_sensitive_count(runner, env_file):
    result = runner.invoke(profile_cmd, [env_file])
    assert "Sensitive keys" in result.output


def test_profile_text_contains_blank_count(runner, env_file):
    result = runner.invoke(profile_cmd, [env_file])
    assert "Blank values" in result.output


def test_profile_json_format_is_valid(runner, env_file):
    result = runner.invoke(profile_cmd, [env_file, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "total_keys" in data
    assert data["total_keys"] == 6


def test_profile_json_has_sensitive_count(runner, env_file):
    result = runner.invoke(profile_cmd, [env_file, "--format", "json"])
    data = json.loads(result.output)
    assert data["sensitive_count"] >= 2


def test_profile_json_has_blank_count(runner, env_file):
    result = runner.invoke(profile_cmd, [env_file, "--format", "json"])
    data = json.loads(result.output)
    assert data["blank_count"] == 1


def test_profile_show_sensitive_lists_keys(runner, env_file):
    result = runner.invoke(profile_cmd, [env_file, "--show-sensitive"])
    assert "APP_SECRET" in result.output or "DATABASE_PASSWORD" in result.output


def test_profile_json_show_sensitive_includes_list(runner, env_file):
    result = runner.invoke(
        profile_cmd, [env_file, "--format", "json", "--show-sensitive"]
    )
    data = json.loads(result.output)
    assert "sensitive_keys" in data
    assert isinstance(data["sensitive_keys"], list)


def test_profile_duplicate_values_reported(runner, env_file):
    result = runner.invoke(profile_cmd, [env_file])
    assert "Duplicate" in result.output
