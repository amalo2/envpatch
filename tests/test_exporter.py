"""Tests for envpatch.exporter module."""
import json

import pytest

from envpatch.differ import diff_envs
from envpatch.exporter import (
    diff_to_dict,
    diff_to_dotenv_patch,
    diff_to_json,
    merge_result_to_dict,
    merge_result_to_json,
)
from envpatch.merger import merge_envs


@pytest.fixture()
def sample_diff():
    old = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
    new = {"HOST": "prod.example.com", "PORT": "5432", "SECRET": "abc123"}
    return diff_envs(old, new)


@pytest.fixture()
def sample_merge():
    base = {"HOST": "localhost", "PORT": "5432"}
    patch = {"SECRET": "abc123", "HOST": "prod.example.com"}
    return merge_envs(base, patch)


def test_diff_to_dict_has_expected_keys(sample_diff):
    result = diff_to_dict(sample_diff)
    assert set(result.keys()) == {"added", "removed", "modified"}


def test_diff_to_dict_added_keys(sample_diff):
    result = diff_to_dict(sample_diff)
    assert result["added"] == {"SECRET": "abc123"}


def test_diff_to_dict_removed_keys(sample_diff):
    result = diff_to_dict(sample_diff)
    assert result["removed"] == {"DEBUG": "true"}


def test_diff_to_dict_modified_keys(sample_diff):
    result = diff_to_dict(sample_diff)
    assert result["modified"]["HOST"] == {"old": "localhost", "new": "prod.example.com"}


def test_diff_to_json_is_valid_json(sample_diff):
    output = diff_to_json(sample_diff)
    parsed = json.loads(output)
    assert isinstance(parsed, dict)


def test_diff_to_json_contains_added(sample_diff):
    output = diff_to_json(sample_diff)
    parsed = json.loads(output)
    assert "SECRET" in parsed["added"]


def test_merge_result_to_dict_structure(sample_merge):
    result = merge_result_to_dict(sample_merge)
    assert "applied" in result
    assert "skipped" in result
    assert "applied_count" in result
    assert "skipped_count" in result


def test_merge_result_to_json_is_valid(sample_merge):
    output = merge_result_to_json(sample_merge)
    parsed = json.loads(output)
    assert isinstance(parsed["applied"], list)


def test_diff_to_dotenv_patch_includes_added(sample_diff):
    patch = diff_to_dotenv_patch(sample_diff)
    assert "SECRET=abc123" in patch


def test_diff_to_dotenv_patch_includes_modified(sample_diff):
    patch = diff_to_dotenv_patch(sample_diff)
    assert "HOST=prod.example.com" in patch


def test_diff_to_dotenv_patch_excludes_removed(sample_diff):
    patch = diff_to_dotenv_patch(sample_diff)
    assert "DEBUG" not in patch


def test_diff_to_dotenv_patch_quotes_values_with_spaces():
    old = {}
    new = {"GREETING": "hello world"}
    diff = diff_envs(old, new)
    patch = diff_to_dotenv_patch(diff)
    assert 'GREETING="hello world"' in patch


def test_diff_to_dotenv_patch_empty_diff():
    diff = diff_envs({"A": "1"}, {"A": "1"})
    patch = diff_to_dotenv_patch(diff)
    assert patch == ""
