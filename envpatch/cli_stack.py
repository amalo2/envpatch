"""CLI command for stacking multiple .env files in priority order."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional, Tuple

import click

from envpatch.stacker import stack_envs


@click.command("stack")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--names",
    default=None,
    help="Comma-separated layer names matching the order of FILES.",
)
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(),
    help="Write merged .env to this path instead of stdout.",
)
@click.option(
    "--summary",
    is_flag=True,
    default=False,
    help="Print a summary of layers and overrides to stderr.",
)
def stack_cmd(
    files: Tuple[str, ...],
    names: Optional[str],
    output: Optional[str],
    summary: bool,
) -> None:
    """Stack multiple .env FILES in order; later files take priority."""
    layer_contents: List[str] = []
    for path in files:
        layer_contents.append(Path(path).read_text())

    layer_names: Optional[List[str]] = None
    if names:
        layer_names = [n.strip() for n in names.split(",")]
        if len(layer_names) != len(files):
            click.echo(
                f"Error: --names has {len(layer_names)} entries but "
                f"{len(files)} files were provided.",
                err=True,
            )
            sys.exit(1)

    result = stack_envs(layer_contents, layer_names)

    merged_lines = [f"{k}={v}" for k, v in result.env.items()]
    merged_text = "\n".join(merged_lines) + "\n" if merged_lines else ""

    if output:
        Path(output).write_text(merged_text)
        click.echo(f"Merged env written to {output}")
    else:
        click.echo(merged_text, nl=False)

    if summary:
        click.echo(result.to_summary(), err=True)
