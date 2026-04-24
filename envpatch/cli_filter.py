"""CLI command: envpatch filter-diff — filter diff output by key pattern or change type."""
from __future__ import annotations

import sys

import click

from envpatch.differ import diff_envs
from envpatch.differ_filter import filter_diff
from envpatch.formats import format_diff
from envpatch.parser import parse_env_file


@click.command("filter-diff")
@click.argument("base", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
@click.option(
    "--pattern", "-p",
    default=None,
    help="Regex pattern to match against key names.",
)
@click.option(
    "--type", "change_types",
    multiple=True,
    type=click.Choice(["added", "removed", "modified"], case_sensitive=False),
    help="Limit to specific change type(s). Repeatable.",
)
@click.option(
    "--include-unchanged",
    is_flag=True,
    default=False,
    help="Include unchanged keys in the filter pool.",
)
@click.option(
    "--format", "fmt",
    default="text",
    type=click.Choice(["text", "json"], case_sensitive=False),
    show_default=True,
    help="Output format.",
)
@click.option(
    "--summary",
    is_flag=True,
    default=False,
    help="Print filter summary instead of full diff.",
)
def filter_cmd(
    base: str,
    target: str,
    pattern: str | None,
    change_types: tuple[str, ...],
    include_unchanged: bool,
    fmt: str,
    summary: bool,
) -> None:
    """Filter diff output between BASE and TARGET .env files."""
    base_env = parse_env_file(base)
    target_env = parse_env_file(target)

    diff = diff_envs(base_env, target_env)

    types_list = list(change_types) if change_types else None
    result = filter_diff(
        diff,
        pattern=pattern,
        change_types=types_list,
        include_unchanged=include_unchanged,
    )

    if summary:
        click.echo(result.to_summary())
        return

    if not result.matched:
        click.echo("No changes matched the given filters.")
        return

    # Build a minimal DiffResult from the matched changes for formatting
    from envpatch.differ import DiffResult
    filtered_diff = DiffResult()
    filtered_diff.changes.extend(result.matched)

    click.echo(format_diff(filtered_diff, fmt=fmt))
