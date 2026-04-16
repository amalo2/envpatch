"""CLI commands for encrypting and decrypting .env files."""
from __future__ import annotations

import click

from envpatch.encryptor import generate_key, encrypt_env, decrypt_env
from envpatch.parser import parse_env_file
from envpatch.patcher import serialize_env


@click.group()
def encrypt_group():
    """Encrypt or decrypt .env values."""


@encrypt_group.command("keygen")
def keygen_cmd():
    """Generate a new encryption key."""
    key = generate_key()
    click.echo(key)


@encrypt_group.command("encrypt")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--key", required=True, envvar="ENVPATCH_KEY", help="Fernet key.")
@click.option("--only", multiple=True, help="Keys to encrypt (default: all).")
@click.option("--output", "-o", default=None, help="Output file (default: stdout).")
def encrypt_cmd(env_file, key, only, output):
    """Encrypt values in an .env file."""
    env = parse_env_file(env_file)
    keys = list(only) if only else None
    result = encrypt_env(env, key, keys=keys)
    merged = {**env, **result.encrypted}
    serialized = serialize_env(merged)
    if output:
        with open(output, "w") as f:
            f.write(serialized)
        click.echo(result.to_summary())
    else:
        click.echo(serialized)


@encrypt_group.command("decrypt")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--key", required=True, envvar="ENVPATCH_KEY", help="Fernet key.")
@click.option("--output", "-o", default=None, help="Output file (default: stdout).")
def decrypt_cmd(env_file, key, output):
    """Decrypt values in an .env file."""
    env = parse_env_file(env_file)
    result = decrypt_env(env, key)
    if result.failed:
        click.echo(f"Warning: {len(result.failed)} key(s) could not be decrypted: {', '.join(result.failed)}", err=True)
    merged = {**env, **result.decrypted}
    serialized = serialize_env(merged)
    if output:
        with open(output, "w") as f:
            f.write(serialized)
        click.echo(result.to_summary())
    else:
        click.echo(serialized)
