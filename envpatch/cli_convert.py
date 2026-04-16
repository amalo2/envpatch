"""CLI commands for env format conversion."""
from __future__ import annotations

import sys
import click

from envpatch.converter import convert_env, from_json


@click.group("convert")
def convert_group():
    """Convert .env files to and from other formats."""


@convert_group.command("to")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--format", "-f", "fmt",
    type=click.Choice(["json", "yaml", "toml"], case_sensitive=False),
    default="json",
    show_default=True,
    help="Target output format.",
)
@click.option("--output", "-o", type=click.Path(), default=None, help="Write output to file.")
def to_cmd(env_file: str, fmt: str, output):
    """Convert ENV_FILE to another format."""
    with open(env_file) as fh:
        content = fh.read()

    result = convert_env(content, fmt)

    for w in result.warnings:
        click.echo(f"Warning: {w}", err=True)

    if output:
        with open(output, "w") as fh:
            fh.write(result.output)
        click.echo(result.to_summary())
    else:
        click.echo(result.output)


@convert_group.command("from")
@click.argument("source_file", type=click.Path(exists=True))
@click.option(
    "--format", "-f", "fmt",
    type=click.Choice(["json"], case_sensitive=False),
    default="json",
    show_default=True,
    help="Source format.",
)
@click.option("--output", "-o", type=click.Path(), default=None, help="Write .env to file.")
def from_cmd(source_file: str, fmt: str, output):
    """Convert SOURCE_FILE back to .env format."""
    with open(source_file) as fh:
        content = fh.read()

    if fmt == "json":
        env_string = from_json(content)
    else:
        click.echo(f"Format {fmt!r} not yet supported for import.", err=True)
        sys.exit(1)

    if output:
        with open(output, "w") as fh:
            fh.write(env_string)
        click.echo(f"Written to {output}")
    else:
        click.echo(env_string, nl=False)
