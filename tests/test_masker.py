import pytest
from envpatch.masker import mask_env, MaskResult, _mask_value


SAMPLE_ENV = {
    "APP_NAME": "myapp",
    "SECRET_KEY": "supersecret",
    "DB_PASSWORD": "hunter2",
    "API_TOKEN": "tok_abc123",
    "PORT": "8080",
}


def test_mask_returns_mask_result():
    result = mask_env(SAMPLE_ENV)
    assert isinstance(result, MaskResult)


def test_sensitive_keys_are_masked():
    result = mask_env(SAMPLE_ENV)
    assert result.masked["SECRET_KEY"] != "supersecret"
    assert result.masked["DB_PASSWORD"] != "hunter2"
    assert result.masked["API_TOKEN"] != "tok_abc123"


def test_non_sensitive_keys_are_unchanged():
    result = mask_env(SAMPLE_ENV)
    assert result.masked["APP_NAME"] == "myapp"
    assert result.masked["PORT"] == "8080"


def test_masked_keys_list_contains_sensitive():
    result = mask_env(SAMPLE_ENV)
    assert "SECRET_KEY" in result.masked_keys
    assert "DB_PASSWORD" in result.masked_keys


def test_visible_keys_list_contains_safe():
    result = mask_env(SAMPLE_ENV)
    assert "APP_NAME" in result.visible_keys
    assert "PORT" in result.visible_keys


def test_masked_count_matches():
    result = mask_env(SAMPLE_ENV)
    assert result.masked_count == len(result.masked_keys)


def test_visible_count_matches():
    result = mask_env(SAMPLE_ENV)
    assert result.visible_count == len(result.visible_keys)


def test_mask_char_applied():
    result = mask_env({"DB_PASSWORD": "secret"}, mask_char="#")
    assert all(c == "#" for c in result.masked["DB_PASSWORD"])


def test_reveal_exposes_prefix():
    result = mask_env({"API_TOKEN": "tok_abc123"}, reveal=3)
    assert result.masked["API_TOKEN"].startswith("tok")
    assert "*" in result.masked["API_TOKEN"]


def test_empty_value_stays_empty():
    result = mask_env({"SECRET_KEY": ""})
    assert result.masked["SECRET_KEY"] == ""


def test_to_summary_returns_string():
    result = mask_env(SAMPLE_ENV)
    summary = result.to_summary()
    assert isinstance(summary, str)
    assert "Masked" in summary


def test_mask_value_full_mask():
    assert _mask_value("hello") == "*****"


def test_mask_value_min_length():
    assert len(_mask_value("hi")) >= 6


def test_extra_patterns_extend_sensitive_detection():
    env = {"MY_INTERNAL_CERT": "certdata", "HOST": "localhost"}
    result = mask_env(env, extra_patterns=["cert"])
    assert result.masked["MY_INTERNAL_CERT"] != "certdata"
    assert result.masked["HOST"] == "localhost"
