"""CLI command for renaming .env keys."""

import sys
from pathlib import Path

import click

from envpatch.renamer import rename_keys


@click.command("rename")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--from",
    "old_key",
    required=True,
    metavar="OLD_KEY",
    help="Key to rename.",
)
@click.option(
    "--to",
    "new_key",
    required=True,
    metavar="NEW_KEY",
    help="New name for the key.",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite new_key if it already exists.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview changes without writing to disk.",
)
@click.option(
    "--in-place",
    is_flag=True,
    default=False,
    help="Write changes back to the source file.",
)
def rename_cmd(
    env_file: str,
    old_key: str,
    new_key: str,
    overwrite: bool,
    dry_run: bool,
    in_place: bool,
) -> None:
    """Rename a key in ENV_FILE."""
    path = Path(env_file)
    content = path.read_text()

    result = rename_keys(content, {old_key: new_key}, overwrite_existing=overwrite)

    click.echo(result.to_summary())

    if dry_run:
        click.echo("\n[dry-run] No changes written.")
        return

    if result.renamed_count == 0:
        click.echo("Nothing to rename.", err=True)
        sys.exit(1)

    if in_place:
        path.write_text(result.output)
        click.echo(f"Written to {path}")
    else:
        click.echo("\n" + result.output)
