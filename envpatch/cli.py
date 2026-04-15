"""CLI entry points for envpatch."""

import sys
import click
from envpatch.parser import parse_env_file
from envpatch.differ import diff_envs
from envpatch.patcher import apply_patch_from_diff, serialize_env
from envpatch.validator import validate_env_string


@click.group()
def cli():
    """envpatch — diff and apply .env file changes safely."""
    pass


@cli.command(name="diff")
@click.argument("base_file", type=click.Path(exists=True))
@click.argument("target_file", type=click.Path(exists=True))
@click.option("--include-unchanged", is_flag=True, default=False, help="Show unchanged keys too.")
def diff_cmd(base_file, target_file, include_unchanged):
    """Show differences between BASE_FILE and TARGET_FILE."""
    base = parse_env_file(base_file)
    target = parse_env_file(target_file)
    result = diff_envs(base, target)
    changes = result.all_changes if include_unchanged else result.changed
    if not changes:
        click.echo("No differences found.")
        return
    for change in changes:
        click.echo(str(change))


@cli.command(name="apply")
@click.argument("base_file", type=click.Path(exists=True))
@click.argument("patch_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default=None, help="Output file (default: stdout).")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
@click.option("--validate", is_flag=True, default=False, help="Validate patch file before applying.")
def apply_cmd(base_file, patch_file, output, overwrite, validate):
    """Apply PATCH_FILE onto BASE_FILE."""
    if validate:
        with open(patch_file) as f:
            raw = f.read()
        result = validate_env_string(raw)
        if not result.is_valid:
            click.echo(str(result), err=True)
            sys.exit(1)

    base = parse_env_file(base_file)
    patch = parse_env_file(patch_file)
    diff = diff_envs(base, patch)
    patched = apply_patch_from_diff(base, diff, overwrite=overwrite)
    serialized = serialize_env(patched)

    if output:
        with open(output, "w") as f:
            f.write(serialized)
        click.echo(f"Written to {output}")
    else:
        click.echo(serialized, nl=False)


@cli.command(name="validate")
@click.argument("env_file", type=click.Path(exists=True))
def validate_cmd(env_file):
    """Validate ENV_FILE for syntax and key naming issues."""
    with open(env_file) as f:
        raw = f.read()
    result = validate_env_string(raw)
    if result.is_valid:
        click.echo(f"{env_file}: OK")
    else:
        click.echo(str(result), err=True)
        sys.exit(1)


def main():
    cli()


if __name__ == "__main__":
    main()
