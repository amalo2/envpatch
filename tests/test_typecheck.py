import pytest
from envpatch.typecheck import typecheck_env, detect_type, TypeCheckResult, TypeHint


def test_typecheck_returns_result():
    result = typecheck_env({"PORT": "8080"})
    assert isinstance(result, TypeCheckResult)


def test_detect_int():
    assert detect_type("42") == "int"


def test_detect_negative_int():
    assert detect_type("-5") == "int"


def test_detect_float():
    assert detect_type("3.14") == "float"


def test_detect_bool_true():
    assert detect_type("true") == "bool"


def test_detect_bool_false():
    assert detect_type("false") == "bool"


def test_detect_bool_yes():
    assert detect_type("yes") == "bool"


def test_detect_url():
    assert detect_type("https://example.com") == "url"


def test_detect_email():
    assert detect_type("user@example.com") == "email"


def test_detect_uuid():
    assert detect_type("550e8400-e29b-41d4-a716-446655440000") == "uuid"


def test_untyped_plain_string():
    assert detect_type("hello world") is None


def test_typed_count():
    result = typecheck_env({"PORT": "8080", "DEBUG": "true", "NAME": "myapp"})
    assert result.typed_count == 2


def test_untyped_count():
    result = typecheck_env({"PORT": "8080", "NAME": "myapp"})
    assert result.untyped_count == 1


def test_untyped_list_contains_key():
    result = typecheck_env({"APP_NAME": "myservice"})
    assert "APP_NAME" in result.untyped


def test_hints_list_contains_typed_key():
    result = typecheck_env({"PORT": "9000"})
    assert any(h.key == "PORT" for h in result.hints)


def test_hint_detected_type_correct():
    result = typecheck_env({"ENABLED": "1"})
    hint = next(h for h in result.hints if h.key == "ENABLED")
    assert hint.detected == "bool"


def test_to_summary_returns_string():
    result = typecheck_env({"PORT": "8080"})
    assert isinstance(result.to_summary(), str)


def test_to_summary_contains_counts():
    result = typecheck_env({"PORT": "8080", "NAME": "app"})
    summary = result.to_summary()
    assert "Typed" in summary and "Untyped" in summary
