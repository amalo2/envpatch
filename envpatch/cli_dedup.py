"""CLI command for deduplicating .env files."""

from __future__ import annotations

import sys

import click

from envpatch.deduplicator import deduplicate_env
from envpatch.patcher import serialize_env


@click.command("dedup")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--keep",
    type=click.Choice(["first", "last"], case_sensitive=False),
    default="last",
    show_default=True,
    help="Which occurrence of a duplicate key to keep.",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    help="Write deduplicated env to this file instead of stdout.",
)
@click.option(
    "--summary", "-s",
    is_flag=True,
    default=False,
    help="Print a summary of resolved duplicates to stderr.",
)
@click.option(
    "--fail-on-duplicates",
    is_flag=True,
    default=False,
    help="Exit with code 1 if any duplicates were found.",
)
def dedup_cmd(
    env_file: str,
    keep: str,
    output: str | None,
    summary: bool,
    fail_on_duplicates: bool,
) -> None:
    """Deduplicate keys in ENV_FILE, keeping the first or last occurrence."""
    with open(env_file, "r", encoding="utf-8") as fh:
        content = fh.read()

    result = deduplicate_env(content, keep=keep)

    serialized = serialize_env(result.env)

    if output:
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(serialized)
        if summary:
            click.echo(result.to_summary(), err=True)
    else:
        click.echo(serialized, nl=False)
        if summary:
            click.echo(result.to_summary(), err=True)

    if fail_on_duplicates and not result.clean:
        sys.exit(1)
