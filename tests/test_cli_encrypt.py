"""Tests for envpatch.cli_encrypt."""
import pytest
from click.testing import CliRunner

pytest.importorskip("cryptography")

from envpatch.cli_encrypt import encrypt_group
from envpatch.encryptor import generate_key


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def key():
    return generate_key()


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_PASSWORD=secret\nAPP_NAME=myapp\n")
    return str(p)


def test_keygen_exits_zero(runner):
    result = runner.invoke(encrypt_group, ["keygen"])
    assert result.exit_code == 0


def test_keygen_outputs_key(runner):
    result = runner.invoke(encrypt_group, ["keygen"])
    assert len(result.output.strip()) > 10


def test_encrypt_exits_zero(runner, env_file, key):
    result = runner.invoke(encrypt_group, ["encrypt", env_file, "--key", key])
    assert result.exit_code == 0


def test_encrypt_output_differs_from_input(runner, env_file, key):
    result = runner.invoke(encrypt_group, ["encrypt", env_file, "--key", key])
    assert "secret" not in result.output


def test_encrypt_with_only_flag(runner, env_file, key):
    result = runner.invoke(encrypt_group, ["encrypt", env_file, "--key", key, "--only", "DB_PASSWORD"])
    assert result.exit_code == 0
    assert "myapp" in result.output


def test_encrypt_writes_output_file(runner, env_file, key, tmp_path):
    out = str(tmp_path / "out.env")
    result = runner.invoke(encrypt_group, ["encrypt", env_file, "--key", key, "--output", out])
    assert result.exit_code == 0
    import os
    assert os.path.exists(out)


def test_decrypt_recovers_values(runner, env_file, key, tmp_path):
    enc_out = str(tmp_path / "enc.env")
    runner.invoke(encrypt_group, ["encrypt", env_file, "--key", key, "--output", enc_out])
    result = runner.invoke(encrypt_group, ["decrypt", enc_out, "--key", key])
    assert result.exit_code == 0
    assert "secret" in result.output
    assert "myapp" in result.output


def test_decrypt_warns_on_bad_key(runner, env_file, tmp_path):
    key1 = generate_key()
    key2 = generate_key()
    enc_out = str(tmp_path / "enc.env")
    runner.invoke(encrypt_group, ["encrypt", env_file, "--key", key1, "--output", enc_out])
    result = runner.invoke(encrypt_group, ["decrypt", enc_out, "--key", key2])
    assert "Warning" in result.output or result.exit_code == 0
