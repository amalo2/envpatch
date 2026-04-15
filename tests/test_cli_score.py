"""Tests for the `envpatch score` CLI command."""
import json
import pytest
from click.testing import CliRunner
from envpatch.cli_score import score_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def clean_env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DATABASE_URL=postgres://localhost/db\nSECRET_KEY=abc123\nPORT=5432\n")
    return str(p)


@pytest.fixture()
def dirty_env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("lowercase_key=value\nEMPTY=\nBAD LINE\n")
    return str(p)


def test_score_exits_zero_for_clean_file(runner, clean_env_file):
    result = runner.invoke(score_cmd, [clean_env_file])
    assert result.exit_code == 0


def test_score_text_contains_score(runner, clean_env_file):
    result = runner.invoke(score_cmd, [clean_env_file])
    assert "Score" in result.output


def test_score_text_contains_grade(runner, clean_env_file):
    result = runner.invoke(score_cmd, [clean_env_file])
    assert "Grade" in result.output


def test_score_json_is_valid_json(runner, clean_env_file):
    result = runner.invoke(score_cmd, [clean_env_file, "--format", "json"])
    data = json.loads(result.output)
    assert "score" in data
    assert "grade" in data


def test_score_json_contains_total_keys(runner, clean_env_file):
    result = runner.invoke(score_cmd, [clean_env_file, "--format", "json"])
    data = json.loads(result.output)
    assert data["total_keys"] == 3


def test_score_json_contains_penalties(runner, dirty_env_file):
    result = runner.invoke(score_cmd, [dirty_env_file, "--format", "json"])
    data = json.loads(result.output)
    assert isinstance(data["penalties"], list)


def test_dirty_file_has_lower_score(runner, clean_env_file, dirty_env_file):
    r_clean = runner.invoke(score_cmd, [clean_env_file, "--format", "json"])
    r_dirty = runner.invoke(score_cmd, [dirty_env_file, "--format", "json"])
    clean_score = json.loads(r_clean.output)["score"]
    dirty_score = json.loads(r_dirty.output)["score"]
    assert dirty_score < clean_score


def test_min_score_passes_when_above_threshold(runner, clean_env_file):
    result = runner.invoke(score_cmd, [clean_env_file, "--min-score", "50"])
    assert result.exit_code == 0


def test_min_score_fails_when_below_threshold(runner, dirty_env_file):
    result = runner.invoke(score_cmd, [dirty_env_file, "--min-score", "99"])
    assert result.exit_code == 1
