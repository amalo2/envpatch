"""CLI sub-command: profile — show statistics for a .env file."""
from __future__ import annotations

import json
import sys

import click

from envpatch.parser import parse_env_file
from envpatch.profiler import profile_env
from envpatch.redactor import redact_env


@click.command("profile")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json"]),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--show-sensitive",
    is_flag=True,
    default=False,
    help="List sensitive key names in output.",
)
def profile_cmd(env_file: str, fmt: str, show_sensitive: bool) -> None:
    """Display a statistical profile of ENV_FILE."""
    try:
        env = parse_env_file(env_file)
    except Exception as exc:  # pragma: no cover
        click.echo(f"Error reading file: {exc}", err=True)
        sys.exit(1)

    result = profile_env(env)

    if fmt == "json":
        data = {
            "total_keys": result.total_keys,
            "sensitive_count": result.sensitive_count,
            "blank_count": result.blank_count,
            "duplicate_value_groups": len(result.duplicate_values),
            "longest_key": result.longest_key,
            "longest_value_key": result.longest_value_key,
        }
        if show_sensitive:
            data["sensitive_keys"] = result.sensitive_keys
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(result.to_summary())
        if show_sensitive and result.sensitive_keys:
            click.echo("\nSensitive keys:")
            for key in result.sensitive_keys:
                click.echo(f"  {key}")
        if result.duplicate_values:
            click.echo("\nDuplicate value groups:")
            for val, keys in result.duplicate_values.items():
                display = repr(val) if len(val) <= 20 else repr(val[:20]) + "..."
                click.echo(f"  {display}: {', '.join(keys)}")
