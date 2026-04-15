"""Tests for envpatch.formats module."""
import json

import pytest

from envpatch.differ import diff_envs
from envpatch.formats import (
    SUPPORTED_FORMATS,
    format_diff,
    register_format,
)


@pytest.fixture()
def simple_diff():
    return diff_envs(
        {"A": "1", "B": "old"},
        {"B": "new", "C": "3"},
    )


def test_supported_formats_contains_defaults():
    assert "text" in SUPPORTED_FORMATS
    assert "json" in SUPPORTED_FORMATS
    assert "patch" in SUPPORTED_FORMATS


def test_format_diff_text_returns_string(simple_diff):
    output = format_diff(simple_diff, fmt="text")
    assert isinstance(output, str)
    assert len(output) > 0


def test_format_diff_json_is_parseable(simple_diff):
    output = format_diff(simple_diff, fmt="json")
    parsed = json.loads(output)
    assert "added" in parsed
    assert "removed" in parsed


def test_format_diff_patch_is_dotenv_style(simple_diff):
    output = format_diff(simple_diff, fmt="patch")
    assert "=" in output


def test_format_diff_unsupported_raises(simple_diff):
    with pytest.raises(ValueError, match="Unsupported format"):
        format_diff(simple_diff, fmt="xml")


def test_format_diff_default_is_text(simple_diff):
    output = format_diff(simple_diff)
    assert isinstance(output, str)


def test_register_custom_format(simple_diff):
    def csv_formatter(diff):
        rows = [f"{k},{c.change_type}" for k, c in diff.changes.items()]
        return "\n".join(rows)

    register_format("csv", csv_formatter)
    assert "csv" in SUPPORTED_FORMATS
    output = format_diff(simple_diff, fmt="csv")
    assert "," in output


def test_register_non_callable_raises():
    with pytest.raises(TypeError, match="callable"):
        register_format("bad", "not_a_function")  # type: ignore[arg-type]


def test_text_format_shows_added_key(simple_diff):
    output = format_diff(simple_diff, fmt="text")
    assert "C" in output


def test_text_format_shows_removed_key(simple_diff):
    output = format_diff(simple_diff, fmt="text")
    assert "A" in output
