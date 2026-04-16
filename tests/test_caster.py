import pytest
from envpatch.caster import cast_env, CastResult


def test_cast_returns_cast_result():
    result = cast_env({"PORT": "8080"})
    assert isinstance(result, CastResult)


def test_int_cast():
    result = cast_env({"PORT": "8080"})
    assert result.cast["PORT"] == 8080
    assert isinstance(result.cast["PORT"], int)


def test_float_cast():
    result = cast_env({"RATIO": "3.14"})
    assert result.cast["RATIO"] == pytest.approx(3.14)


def test_bool_true_cast():
    result = cast_env({"DEBUG": "true"})
    assert result.cast["DEBUG"] is True


def test_bool_false_cast():
    result = cast_env({"DEBUG": "false"})
    assert result.cast["DEBUG"] is False


def test_bool_case_insensitive():
    result = cast_env({"FLAG": "TRUE"})
    assert result.cast["FLAG"] is True


def test_string_unchanged():
    result = cast_env({"NAME": "hello"})
    assert result.cast["NAME"] == "hello"


def test_list_cast():
    result = cast_env({"HOSTS": "[a, b, c]"})
    assert result.cast["HOSTS"] == ["a", "b", "c"]


def test_empty_list_cast():
    result = cast_env({"ITEMS": "[]"})
    assert result.cast["ITEMS"] == []


def test_cast_count():
    result = cast_env({"A": "1", "B": "2"})
    assert result.cast_count == 2


def test_failed_count_zero_for_clean_env():
    result = cast_env({"X": "hello"})
    assert result.failed_count == 0


def test_selective_cast_by_keys():
    result = cast_env({"PORT": "9000", "NAME": "app"}, keys=["PORT"])
    assert isinstance(result.cast["PORT"], int)
    assert result.cast["NAME"] == "app"


def test_to_summary_contains_counts():
    result = cast_env({"A": "1", "B": "text"})
    summary = result.to_summary()
    assert "2" in summary
