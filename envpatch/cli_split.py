"""CLI command for splitting .env files by prefix."""
from __future__ import annotations

import os

import click

from envpatch.splitter import split_env
from envpatch.patcher import serialize_env


@click.command("split")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--prefix",
    "prefixes",
    multiple=True,
    required=True,
    help="Prefix to split on (repeatable). E.g. --prefix DB_ --prefix AWS_",
)
@click.option(
    "--output-dir",
    default=".",
    show_default=True,
    help="Directory to write segment files into.",
)
@click.option(
    "--strip-prefix",
    is_flag=True,
    default=False,
    help="Remove the matched prefix from keys in output files.",
)
@click.option(
    "--no-unmatched",
    is_flag=True,
    default=False,
    help="Discard keys that do not match any prefix.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Print summary without writing files.",
)
def split_cmd(
    env_file: str,
    prefixes: tuple,
    output_dir: str,
    strip_prefix: bool,
    no_unmatched: bool,
    dry_run: bool,
) -> None:
    """Split ENV_FILE into separate files by key prefix."""
    with open(env_file) as fh:
        content = fh.read()

    result = split_env(
        content,
        list(prefixes),
        strip_prefix=strip_prefix,
        keep_unmatched=not no_unmatched,
    )

    click.echo(result.to_summary())

    if dry_run:
        return

    os.makedirs(output_dir, exist_ok=True)

    for prefix, keys in result.segments.items():
        safe_name = prefix.lower().rstrip("_")
        out_path = os.path.join(output_dir, f"{safe_name}.env")
        with open(out_path, "w") as fh:
            fh.write(serialize_env(keys))
        click.echo(f"Written: {out_path}")

    if result.unmatched:
        out_path = os.path.join(output_dir, "unmatched.env")
        with open(out_path, "w") as fh:
            fh.write(serialize_env(result.unmatched))
        click.echo(f"Written: {out_path}")
