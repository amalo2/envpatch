"""Tests for envpatch.interpolator."""
import pytest
from envpatch.interpolator import interpolate_env, InterpolateResult


def test_returns_interpolate_result():
    result = interpolate_env({"A": "1"})
    assert isinstance(result, InterpolateResult)


def test_plain_value_unchanged():
    result = interpolate_env({"HOST": "localhost"})
    assert result.output["HOST"] == "localhost"


def test_dollar_brace_substitution():
    env = {"BASE": "/app", "LOG": "${BASE}/logs"}
    result = interpolate_env(env)
    assert result.output["LOG"] == "/app/logs"


def test_bare_dollar_substitution():
    env = {"USER": "alice", "GREETING": "Hello $USER"}
    result = interpolate_env(env)
    assert result.output["GREETING"] == "Hello alice"


def test_resolved_list_populated():
    env = {"PORT": "8080", "URL": "http://host:${PORT}"}
    result = interpolate_env(env)
    assert "PORT" in result.resolved


def test_unresolved_left_as_is():
    env = {"URL": "http://${HOST}"}
    result = interpolate_env(env)
    assert result.output["URL"] == "http://${HOST}"


def test_unresolved_list_populated():
    env = {"URL": "http://${MISSING}"}
    result = interpolate_env(env)
    assert "MISSING" in result.unresolved


def test_is_complete_true_when_all_resolved():
    env = {"A": "1", "B": "$A"}
    result = interpolate_env(env)
    assert result.is_complete is True


def test_is_complete_false_when_unresolved():
    env = {"B": "$MISSING"}
    result = interpolate_env(env)
    assert result.is_complete is False


def test_context_used_for_resolution():
    env = {"FULL_URL": "${SCHEME}://localhost"}
    result = interpolate_env(env, context={"SCHEME": "https"})
    assert result.output["FULL_URL"] == "https://localhost"


def test_strict_mode_raises_on_missing():
    env = {"X": "${UNDEFINED}"}
    with pytest.raises(KeyError, match="UNDEFINED"):
        interpolate_env(env, strict=True)


def test_to_summary_contains_counts():
    env = {"A": "$B", "C": "$MISSING"}
    result = interpolate_env(env)
    summary = result.to_summary()
    assert "Resolved" in summary
    assert "Unresolved" in summary
