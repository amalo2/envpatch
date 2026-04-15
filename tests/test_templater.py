"""Tests for envpatch.templater module."""

import pytest
from envpatch.templater import render_template, RenderResult


SIMPLE_TEMPLATE = """APP_NAME=${APP_NAME}
DEBUG=${DEBUG:false}
SECRET_KEY=${SECRET_KEY}
"""


def test_render_returns_render_result():
    result = render_template("KEY=${VAL}", {"VAL": "hello"})
    assert isinstance(result, RenderResult)


def test_resolved_variable_substituted():
    result = render_template("KEY=${VAL}", {"VAL": "world"})
    assert result.output == "KEY=world"


def test_resolved_key_tracked():
    result = render_template("KEY=${VAL}", {"VAL": "world"})
    assert "VAL" in result.resolved


def test_default_used_when_key_missing():
    result = render_template("DEBUG=${DEBUG:false}", {})
    assert result.output == "DEBUG=false"


def test_default_key_tracked_in_used_defaults():
    result = render_template("DEBUG=${DEBUG:false}", {})
    assert "DEBUG" in result.used_defaults


def test_unresolved_variable_left_in_place():
    result = render_template("KEY=${MISSING}", {})
    assert "${MISSING}" in result.output


def test_unresolved_key_tracked():
    result = render_template("KEY=${MISSING}", {})
    assert "MISSING" in result.unresolved


def test_is_complete_true_when_all_resolved():
    result = render_template("A=${X}\nB=${Y:default}", {"X": "1"})
    assert result.is_complete is True


def test_is_complete_false_when_unresolved():
    result = render_template("A=${MISSING}", {})
    assert result.is_complete is False


def test_strict_mode_raises_on_missing_variable():
    with pytest.raises(ValueError, match="Unresolved template variable: MISSING"):
        render_template("KEY=${MISSING}", {}, strict=True)


def test_strict_mode_allows_defaults():
    result = render_template("KEY=${VAR:fallback}", {}, strict=True)
    assert result.output == "KEY=fallback"


def test_multiple_variables_in_template():
    ctx = {"APP_NAME": "myapp", "SECRET_KEY": "abc123"}
    result = render_template(SIMPLE_TEMPLATE, ctx)
    assert "APP_NAME=myapp" in result.output
    assert "DEBUG=false" in result.output
    assert "SECRET_KEY=abc123" in result.output


def test_to_summary_contains_resolved():
    result = render_template("A=${X}", {"X": "1"})
    summary = result.to_summary()
    assert "Resolved" in summary


def test_to_summary_contains_unresolved():
    result = render_template("A=${MISSING}", {})
    summary = result.to_summary()
    assert "Unresolved" in summary


def test_to_summary_no_vars_message():
    result = render_template("PLAIN=value", {})
    assert result.to_summary() == "No variables found."


def test_render_template_file(tmp_path):
    from envpatch.templater import render_template_file
    tpl = tmp_path / "template.env"
    tpl.write_text("HOST=${HOST:localhost}\nPORT=${PORT}\n")
    result = render_template_file(str(tpl), {"PORT": "8080"})
    assert "HOST=localhost" in result.output
    assert "PORT=8080" in result.output
