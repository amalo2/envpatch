"""CLI command: envpatch archive — bundle .env files into a timestamped zip."""

from __future__ import annotations

import click

from envpatch.archiver import archive_envs


@click.command("archive")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--output-dir",
    "-o",
    default=".",
    show_default=True,
    help="Directory to write the archive into.",
)
@click.option(
    "--label",
    "-l",
    default=None,
    help="Optional label embedded in the archive filename.",
)
@click.option(
    "--no-metadata",
    is_flag=True,
    default=False,
    help="Omit the _meta.json file from the archive.",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    default=False,
    help="Suppress summary output.",
)
def archive_cmd(
    files: tuple,
    output_dir: str,
    label: str | None,
    no_metadata: bool,
    quiet: bool,
) -> None:
    """Bundle one or more .env FILES into a timestamped zip archive."""
    result = archive_envs(
        list(files),
        output_dir=output_dir,
        label=label,
        include_metadata=not no_metadata,
    )

    if not quiet:
        click.echo(result.to_summary())

    if result.skipped_count and not quiet:
        click.echo(f"\nWarning: {result.skipped_count} file(s) were skipped.", err=True)
        for s in result.skipped:
            click.echo(f"  - {s}", err=True)
