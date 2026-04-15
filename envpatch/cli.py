"""Command-line interface for envpatch."""

import sys
from pathlib import Path

import click

from envpatch.parser import parse_env_file
from envpatch.differ import diff_envs
from envpatch.patcher import apply_patch_from_diff, serialize_env


@click.group()
@click.version_option()
def cli():
    """envpatch — diff and apply .env file changes across environments."""


@cli.command("diff")
@click.argument("base", type=click.Path(exists=True, dir_okay=False))
@click.argument("target", type=click.Path(exists=True, dir_okay=False))
@click.option("--show-unchanged", is_flag=True, default=False, help="Include unchanged keys in output.")
def diff_cmd(base, target, show_unchanged):
    """Show differences between BASE and TARGET .env files."""
    base_env = parse_env_file(base)
    target_env = parse_env_file(target)
    result = diff_envs(base_env, target_env)

    changes = list(result.changes(include_unchanged=show_unchanged))
    if not changes:
        click.echo("No differences found.")
        return

    for change in changes:
        click.echo(str(change))


@cli.command("apply")
@click.argument("base", type=click.Path(exists=True, dir_okay=False))
@click.argument("patch", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--output", "-o",
    type=click.Path(dir_okay=False),
    default=None,
    help="Output file path. Defaults to overwriting BASE.",
)
@click.option("--dry-run", is_flag=True, default=False, help="Print result without writing.")
def apply_cmd(base, patch, output, dry_run):
    """Apply PATCH .env onto BASE without overwriting existing keys."""
    base_env = parse_env_file(base)
    patch_env = parse_env_file(patch)
    result = diff_envs(base_env, patch_env)
    patched = apply_patch_from_diff(base_env, result)
    serialized = serialize_env(patched)

    if dry_run:
        click.echo(serialized)
        return

    out_path = output or base
    Path(out_path).write_text(serialized)
    click.echo(f"Patched env written to {out_path}")


def main():
    cli(prog_name="envpatch")


if __name__ == "__main__":
    main()
