"""Tests for envpatch.scorer."""
import pytest
from envpatch.scorer import score_env, ScoreResult


CLEAN_ENV = """DATABASE_URL=postgres://localhost/mydb
SECRET_KEY=supersecret
DEBUG=false
PORT=8080
"""

DIRTY_ENV = """database_url=postgres://localhost/mydb
SECRET_KEY=
BAD LINE
PORT=8080
"""


def test_score_returns_score_result():
    result = score_env(CLEAN_ENV)
    assert isinstance(result, ScoreResult)


def test_clean_env_scores_100():
    result = score_env(CLEAN_ENV)
    assert result.score == 100


def test_clean_env_grade_is_a():
    result = score_env(CLEAN_ENV)
    assert result.grade == "A"


def test_dirty_env_score_is_lower():
    clean = score_env(CLEAN_ENV)
    dirty = score_env(DIRTY_ENV)
    assert dirty.score < clean.score


def test_dirty_env_has_penalties():
    result = score_env(DIRTY_ENV)
    assert len(result.penalties) > 0


def test_total_keys_reflects_profile():
    result = score_env(CLEAN_ENV)
    assert result.total_keys == 4


def test_blank_value_reduces_score():
    env = "KEY=\nOTHER=value\n"
    result = score_env(env)
    assert result.score < 100
    assert any("blank" in p for p in result.penalties)


def test_lint_warning_reduces_score():
    env = "lowercase_key=value\n"
    result = score_env(env)
    assert result.score < 100


def test_score_never_goes_below_zero():
    terrible = "\n".join([f"bad line {i}" for i in range(20)])
    result = score_env(terrible)
    assert result.score >= 0


def test_grade_f_for_very_low_score():
    # force a low score by checking grade boundaries
    r = ScoreResult(total_keys=0, score=20)
    assert r.grade == "F"


def test_grade_b_for_mid_score():
    r = ScoreResult(total_keys=0, score=80)
    assert r.grade == "B"


def test_to_summary_contains_score():
    result = score_env(CLEAN_ENV)
    summary = result.to_summary()
    assert "100" in summary


def test_to_summary_contains_grade():
    result = score_env(CLEAN_ENV)
    summary = result.to_summary()
    assert "Grade" in summary


def test_to_summary_lists_penalties():
    result = score_env(DIRTY_ENV)
    summary = result.to_summary()
    assert "Penalties" in summary
