"""CLI command for stripping keys from a .env file."""
from __future__ import annotations
import click

from envpatch.stripper import strip_keys


@click.command("strip")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("-k", "--key", "keys", multiple=True, help="Explicit key to strip.")
@click.option("-p", "--pattern", "patterns", multiple=True, help="Regex pattern to match keys.")
@click.option("--in-place", is_flag=True, default=False, help="Overwrite the file in place.")
@click.option("--summary", is_flag=True, default=False, help="Print summary after stripping.")
def strip_cmd(
    env_file: str,
    keys: tuple[str, ...],
    patterns: tuple[str, ...],
    in_place: bool,
    summary: bool,
) -> None:
    """Strip keys from ENV_FILE by name or regex pattern."""
    with open(env_file) as f:
        content = f.read()

    result = strip_keys(content, keys=list(keys), patterns=list(patterns))

    if in_place:
        with open(env_file, "w") as f:
            f.write(result.output)
    else:
        click.echo(result.output, nl=False)

    if summary:
        click.echo(result.to_summary(), err=True)
