"""Tests for envpatch.differ_patch — patch generation from DiffResult."""

import pytest

from envpatch.differ import DiffResult, EnvChange
from envpatch.differ_patch import PatchGenResult, generate_patch


def _make_diff(*changes: EnvChange) -> DiffResult:
    return DiffResult(changes=list(changes))


def _change(key: str, change_type: str, old=None, new=None) -> EnvChange:
    return EnvChange(key=key, change_type=change_type, old_value=old, new_value=new)


# --- return type ---

def test_generate_patch_returns_patch_gen_result():
    diff = _make_diff()
    result = generate_patch(diff)
    assert isinstance(result, PatchGenResult)


def test_empty_diff_produces_empty_patch():
    diff = _make_diff()
    result = generate_patch(diff)
    assert result.patch_env == ""
    assert result.included_count == 0


# --- added keys ---

def test_added_key_included_by_default():
    diff = _make_diff(_change("NEW_KEY", "added", new="hello"))
    result = generate_patch(diff)
    assert "NEW_KEY=hello" in result.patch_env


def test_added_key_excluded_when_flag_false():
    diff = _make_diff(_change("NEW_KEY", "added", new="hello"))
    result = generate_patch(diff, include_added=False)
    assert "NEW_KEY" not in result.patch_env
    assert result.skipped_count == 1


# --- modified keys ---

def test_modified_key_uses_new_value():
    diff = _make_diff(_change("HOST", "modified", old="localhost", new="prod.example.com"))
    result = generate_patch(diff)
    assert "HOST=prod.example.com" in result.patch_env


def test_modified_key_excluded_when_flag_false():
    diff = _make_diff(_change("HOST", "modified", old="localhost", new="prod.example.com"))
    result = generate_patch(diff, include_modified=False)
    assert "HOST" not in result.patch_env
    assert result.skipped_count == 1


# --- removed keys ---

def test_removed_key_excluded_by_default():
    diff = _make_diff(_change("OLD_KEY", "removed", old="value"))
    result = generate_patch(diff)
    assert "OLD_KEY" not in result.patch_env
    assert result.skipped_count == 1


def test_removed_key_included_as_comment_when_flag_set():
    diff = _make_diff(_change("OLD_KEY", "removed", old="value"))
    result = generate_patch(diff, include_removed=True)
    assert "OLD_KEY" in result.patch_env
    assert "(removed)" in result.patch_env


# --- comments ---

def test_prefix_comments_present_by_default():
    diff = _make_diff(_change("FOO", "added", new="bar"))
    result = generate_patch(diff)
    assert "# ADDED: FOO" in result.patch_env


def test_prefix_comments_suppressed_when_flag_false():
    diff = _make_diff(_change("FOO", "added", new="bar"))
    result = generate_patch(diff, prefix_comments=False)
    assert "# ADDED" not in result.patch_env
    assert "FOO=bar" in result.patch_env


# --- counts and metadata ---

def test_included_count_matches_emitted_entries():
    diff = _make_diff(
        _change("A", "added", new="1"),
        _change("B", "modified", old="x", new="y"),
        _change("C", "removed", old="z"),
    )
    result = generate_patch(diff, include_removed=True)
    assert result.included_count == 3


def test_change_types_reflect_included_types():
    diff = _make_diff(
        _change("A", "added", new="1"),
        _change("B", "modified", old="x", new="y"),
    )
    result = generate_patch(diff)
    assert "added" in result.change_types
    assert "modified" in result.change_types


def test_to_summary_returns_string():
    diff = _make_diff(_change("X", "added", new="1"))
    result = generate_patch(diff)
    summary = result.to_summary()
    assert isinstance(summary, str)
    assert "included" in summary
