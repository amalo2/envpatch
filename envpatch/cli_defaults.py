"""CLI command: envpatch defaults — fill missing keys from a defaults file."""
import click

from envpatch.defaults import apply_defaults
from envpatch.patcher import serialize_env


@click.command("defaults")
@click.argument("target", type=click.Path(exists=True))
@click.argument("defaults_file", type=click.Path(exists=True), metavar="DEFAULTS")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite keys already present in target.",
)
@click.option(
    "--summary",
    is_flag=True,
    default=False,
    help="Print a summary instead of the merged env.",
)
@click.option(
    "--in-place",
    "in_place",
    is_flag=True,
    default=False,
    help="Write result back to TARGET file.",
)
def defaults_cmd(
    target: str,
    defaults_file: str,
    overwrite: bool,
    summary: bool,
    in_place: bool,
) -> None:
    """Fill missing keys in TARGET from DEFAULTS without touching existing values."""
    with open(target) as fh:
        target_text = fh.read()
    with open(defaults_file) as fh:
        defaults_text = fh.read()

    result = apply_defaults(target_text, defaults_text, overwrite=overwrite)

    if summary:
        click.echo(result.to_summary())
        if result.applied:
            click.echo("Filled: " + ", ".join(result.applied))
        if result.skipped:
            click.echo("Skipped: " + ", ".join(result.skipped))
        return

    merged_text = serialize_env(result.filled)

    if in_place:
        with open(target, "w") as fh:
            fh.write(merged_text)
        click.echo(f"Written to {target}")
    else:
        click.echo(merged_text, nl=False)
