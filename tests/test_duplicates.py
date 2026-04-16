import pytest
from envpatch.duplicates import find_duplicates, DuplicateResult


SIMPLE_ENV = """KEY_A=1
KEY_B=2
KEY_C=3
"""

DUPE_ENV = """KEY_A=first
KEY_B=only
KEY_A=second
"""

MULTI_DUPE_ENV = """KEY_A=1
KEY_A=2
KEY_B=x
KEY_B=y
KEY_B=z
"""


def test_find_duplicates_returns_result():
    result = find_duplicates(SIMPLE_ENV)
    assert isinstance(result, DuplicateResult)


def test_no_duplicates_in_clean_env():
    result = find_duplicates(SIMPLE_ENV)
    assert not result.has_duplicates


def test_duplicate_count_zero_for_clean_env():
    result = find_duplicates(SIMPLE_ENV)
    assert result.duplicate_count == 0


def test_detects_single_duplicate_key():
    result = find_duplicates(DUPE_ENV)
    assert "KEY_A" in result.duplicates


def test_duplicate_line_numbers_recorded():
    result = find_duplicates(DUPE_ENV)
    assert result.duplicates["KEY_A"] == [1, 3]


def test_non_duplicate_key_excluded():
    result = find_duplicates(DUPE_ENV)
    assert "KEY_B" not in result.duplicates


def test_multiple_duplicate_keys_detected():
    result = find_duplicates(MULTI_DUPE_ENV)
    assert result.duplicate_count == 2


def test_multi_occurrence_line_numbers():
    result = find_duplicates(MULTI_DUPE_ENV)
    assert result.duplicates["KEY_B"] == [3, 4, 5]


def test_env_contains_last_value_for_duplicate():
    result = find_duplicates(DUPE_ENV)
    assert result.env["KEY_A"] == "second"


def test_has_duplicates_true_when_dupes_found():
    result = find_duplicates(DUPE_ENV)
    assert result.has_duplicates


def test_summary_no_duplicates():
    result = find_duplicates(SIMPLE_ENV)
    assert "No duplicate" in result.to_summary()


def test_summary_lists_duplicate_key():
    result = find_duplicates(DUPE_ENV)
    summary = result.to_summary()
    assert "KEY_A" in summary


def test_comments_and_blanks_ignored():
    env = "# comment\n\nKEY=val\nKEY=val2\n"
    result = find_duplicates(env)
    assert "KEY" in result.duplicates
    assert result.duplicate_count == 1
