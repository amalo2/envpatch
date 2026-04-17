"""CLI command: envpatch require — check required keys are present."""
from __future__ import annotations

import sys
import click

from envpatch.requirer import require_keys


@click.command("require")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "-k",
    "--key",
    "keys",
    multiple=True,
    required=True,
    help="Required key name (repeatable).",
)
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero if any key is missing.")
def require_cmd(env_file: str, keys: tuple, strict: bool) -> None:
    """Verify that required keys exist in ENV_FILE."""
    with open(env_file) as fh:
        content = fh.read()

    result = require_keys(content, list(keys))
    click.echo(result.to_summary())

    if strict and not result.is_satisfied:
        sys.exit(1)
