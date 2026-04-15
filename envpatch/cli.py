"""CLI entry point for envpatch."""

from __future__ import annotations

import click

from envpatch.differ import diff_envs
from envpatch.formats import format_diff
from envpatch.merger import merge_envs
from envpatch.patcher import apply_patch_from_diff, serialize_env
from envpatch.parser import parse_env_file
from envpatch.snapshot import capture_snapshot, restore_snapshot, Snapshot
from envpatch.validator import validate_env_file


@click.group()
def cli() -> None:
    """envpatch — diff and apply .env changes safely."""


@cli.command(name="diff")
@click.argument("base")
@click.argument("head")
@click.option("--format", "fmt", default="text", show_default=True, help="Output format: text, json, patch")
@click.option("--include-unchanged", is_flag=True, default=False, help="Include unchanged keys in output")
def diff_cmd(base: str, head: str, fmt: str, include_unchanged: bool) -> None:
    """Show diff between BASE and HEAD .env files."""
    base_env = parse_env_file(base)
    head_env = parse_env_file(head)
    result = diff_envs(base_env, head_env, include_unchanged=include_unchanged)
    click.echo(format_diff(result, fmt=fmt))


@cli.command(name="apply")
@click.argument("base")
@click.argument("patch")
@click.option("--output", "-o", default=None, help="Write result to file instead of stdout")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys")
def apply_cmd(base: str, patch: str, output: str | None, overwrite: bool) -> None:
    """Apply PATCH .env onto BASE .env."""
    base_env = parse_env_file(base)
    patch_env = parse_env_file(patch)
    diff = diff_envs(base_env, patch_env)
    updated = apply_patch_from_diff(base_env, diff, overwrite=overwrite)
    content = serialize_env(updated)
    if output:
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(content)
        click.echo(f"Written to {output}")
    else:
        click.echo(content)


@cli.command(name="validate")
@click.argument("env_file")
def validate_cmd(env_file: str) -> None:
    """Validate ENV_FILE for syntax errors."""
    result = validate_env_file(env_file)
    if result.is_valid:
        click.echo("OK")
    else:
        for err in result.errors:
            click.echo(str(err), err=True)
        raise SystemExit(1)


@cli.command(name="snapshot")
@click.argument("env_file")
@click.argument("snapshot_out")
def snapshot_cmd(env_file: str, snapshot_out: str) -> None:
    """Capture a snapshot of ENV_FILE and save to SNAPSHOT_OUT."""
    snap = capture_snapshot(env_file, snapshot_path=snapshot_out)
    click.echo(f"Snapshot saved: {len(snap.data)} keys captured to {snapshot_out}")


@cli.command(name="restore")
@click.argument("snapshot_in")
@click.option("--output", "-o", default=None, help="Target .env path (defaults to original source)")
def restore_cmd(snapshot_in: str, output: str | None) -> None:
    """Restore a .env file from SNAPSHOT_IN."""
    snap = Snapshot.load(snapshot_in)
    target = restore_snapshot(snap, target_path=output)
    click.echo(f"Restored {len(snap.data)} keys to {target}")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
