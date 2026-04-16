import sys
import click

from envpatch.duplicates import find_duplicates


@click.command("duplicates")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--exit-nonzero", is_flag=True, default=False,
              help="Exit with code 1 if duplicates are found.")
def duplicates_cmd(env_file: str, exit_nonzero: bool) -> None:
    """Report duplicate keys in an .env file."""
    with open(env_file, "r") as fh:
        content = fh.read()

    result = find_duplicates(content)
    click.echo(result.to_summary())

    if exit_nonzero and result.has_duplicates:
        sys.exit(1)
