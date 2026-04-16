"""Tests for envpatch.encryptor."""
import pytest

pytest.importorskip("cryptography")

from envpatch.encryptor import (
    generate_key,
    encrypt_env,
    decrypt_env,
    EncryptResult,
    DecryptResult,
)


@pytest.fixture
def key():
    return generate_key()


@pytest.fixture
def sample_env():
    return {"DB_PASSWORD": "secret", "API_KEY": "abc123", "APP_NAME": "myapp"}


def test_generate_key_returns_string(key):
    assert isinstance(key, str)
    assert len(key) > 0


def test_encrypt_returns_encrypt_result(key, sample_env):
    result = encrypt_env(sample_env, key)
    assert isinstance(result, EncryptResult)


def test_all_keys_encrypted_by_default(key, sample_env):
    result = encrypt_env(sample_env, key)
    assert result.encrypted_count == len(sample_env)
    assert result.skipped_count == 0


def test_encrypted_values_differ_from_originals(key, sample_env):
    result = encrypt_env(sample_env, key)
    for k, v in result.encrypted.items():
        assert v != sample_env[k]


def test_selective_encryption_skips_others(key, sample_env):
    result = encrypt_env(sample_env, key, keys=["DB_PASSWORD"])
    assert "DB_PASSWORD" in result.encrypted
    assert "APP_NAME" in result.skipped
    assert result.encrypted_count == 1
    assert result.skipped_count == 2


def test_decrypt_returns_decrypt_result(key, sample_env):
    enc = encrypt_env(sample_env, key)
    result = decrypt_env(enc.encrypted, key)
    assert isinstance(result, DecryptResult)


def test_decrypt_recovers_original_values(key, sample_env):
    enc = encrypt_env(sample_env, key)
    dec = decrypt_env(enc.encrypted, key)
    for k in sample_env:
        assert dec.decrypted[k] == sample_env[k]


def test_decrypt_fails_with_wrong_key(sample_env):
    key1 = generate_key()
    key2 = generate_key()
    enc = encrypt_env(sample_env, key1)
    dec = decrypt_env(enc.encrypted, key2)
    assert len(dec.failed) == len(sample_env)
    assert dec.decrypted_count == 0


def test_decrypt_fails_for_invalid_token(key):
    bad_env = {"SECRET": "not-encrypted-value"}
    dec = decrypt_env(bad_env, key)
    assert "SECRET" in dec.failed


def test_to_summary_encrypt(key, sample_env):
    result = encrypt_env(sample_env, key)
    summary = result.to_summary()
    assert "3" in summary


def test_to_summary_decrypt(key, sample_env):
    enc = encrypt_env(sample_env, key)
    dec = decrypt_env(enc.encrypted, key)
    summary = dec.to_summary()
    assert "3" in summary
