"""CLI command for injecting .env variables into the current shell environment."""
from __future__ import annotations

import sys
from typing import Optional

import click

from envpatch.injector import inject_env


@click.command("inject")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing environment variables.",
)
@click.option(
    "--prefix",
    default=None,
    metavar="PREFIX",
    help="Prepend PREFIX to every injected key.",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "export", "json"], case_sensitive=False),
    default="text",
    show_default=True,
    help="Output format.",
)
def inject_cmd(
    env_file: str,
    overwrite: bool,
    prefix: Optional[str],
    fmt: str,
) -> None:
    """Inject variables from ENV_FILE into the current process environment.

    Use --format export to emit shell-compatible export statements that can be
    eval'd: ``eval $(envpatch inject .env --format export)``
    """
    raw = click.open_file(env_file).read()
    # Inject into a copy so we can report without polluting the test process.
    import os
    result = inject_env(raw, overwrite=overwrite, prefix=prefix, target=dict(os.environ))

    if fmt == "json":
        import json
        click.echo(
            json.dumps(
                {
                    "injected": result.injected,
                    "skipped": result.skipped,
                    "injected_count": result.injected_count,
                    "skipped_count": result.skipped_count,
                },
                indent=2,
            )
        )
    elif fmt == "export":
        for key in result.injected:
            value = result.env.get(key, "")
            click.echo(f"export {key}={value!r}")
    else:
        click.echo(result.to_summary())
        if result.injected:
            click.echo("  Injected: " + ", ".join(result.injected))
        if result.skipped:
            click.echo("  Skipped:  " + ", ".join(result.skipped))
