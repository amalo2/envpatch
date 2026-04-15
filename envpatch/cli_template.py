"""CLI commands for template rendering, registered into the main envpatch CLI."""

import sys
from pathlib import Path

import click

from envpatch.parser import parse_env_file
from envpatch.templater import render_template_file


@click.command("render")
@click.argument("template", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--context",
    "-c",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help=".env file to use as variable context.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False),
    default=None,
    help="Write rendered output to file instead of stdout.",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Fail if any template variables are unresolved.",
)
@click.option(
    "--summary",
    is_flag=True,
    default=False,
    help="Print resolution summary to stderr.",
)
def render_cmd(template: str, context: str, output: str, strict: bool, summary: bool) -> None:
    """Render a .env TEMPLATE by substituting ${VAR} placeholders.

    Variables are sourced from the --context .env file.
    Placeholders support defaults: ${VAR:default_value}.
    """
    ctx: dict = {}
    if context:
        ctx = parse_env_file(context)

    try:
        result = render_template_file(template, ctx, strict=strict)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if summary:
        click.echo(result.to_summary(), err=True)

    if output:
        Path(output).write_text(result.output)
        click.echo(f"Rendered output written to {output}", err=True)
    else:
        click.echo(result.output, nl=False)

    if not result.is_complete and not strict:
        unresolved = ", ".join(result.unresolved)
        click.echo(f"Warning: unresolved variables: {unresolved}", err=True)
        sys.exit(2)
