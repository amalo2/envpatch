"""CLI command for linting .env files."""
from __future__ import annotations

import sys

import click

from envpatch.linter import lint_env


@click.command("lint")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with non-zero status on warnings as well as errors.",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    default=False,
    help="Suppress output; only use exit code.",
)
def lint_cmd(env_file: str, strict: bool, quiet: bool) -> None:
    """Lint ENV_FILE for style and best-practice issues."""
    with open(env_file, "r", encoding="utf-8") as fh:
        source = fh.read()

    result = lint_env(source)

    if not quiet:
        click.echo(result.to_summary())

    if result.error_count > 0:
        sys.exit(1)

    if strict and result.warning_count > 0:
        sys.exit(1)
