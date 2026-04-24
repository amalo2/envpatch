"""CLI command for sanitizing .env file values."""

from __future__ import annotations

import sys

import click

from envpatch.sanitizer import sanitize_env
from envpatch.patcher import serialize_env


@click.command("sanitize")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--key",
    "keys",
    multiple=True,
    help="Specific key(s) to sanitize. Repeatable. Default: all keys.",
)
@click.option(
    "--replacement",
    default="",
    show_default=True,
    help="Character to substitute for unsafe bytes (default: remove).",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="Write sanitized env to this file instead of stdout.",
)
@click.option(
    "--summary",
    is_flag=True,
    default=False,
    help="Print a summary of changes to stderr.",
)
def sanitize_cmd(
    env_file: str,
    keys: tuple,
    replacement: str,
    output: str | None,
    summary: bool,
) -> None:
    """Remove or replace unsafe control characters from .env values."""
    with open(env_file) as fh:
        source = fh.read()

    result = sanitize_env(
        source,
        keys=list(keys) if keys else None,
        replacement=replacement,
    )

    serialized = serialize_env(result.env)

    if output:
        with open(output, "w") as fh:
            fh.write(serialized)
    else:
        click.echo(serialized, nl=False)

    if summary:
        click.echo(result.to_summary(), err=True)

    if result.sanitized_count > 0 and not output:
        sys.exit(0)
