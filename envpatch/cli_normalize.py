"""CLI command for normalizing .env keys."""
import click

from envpatch.normalizer import normalize_env
from envpatch.patcher import serialize_env


@click.command("normalize")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default=None, help="Write result to file.")
@click.option("--summary", "show_summary", is_flag=True, default=False, help="Print summary.")
def normalize_cmd(env_file: str, output: str, show_summary: bool) -> None:
    """Normalize all keys in ENV_FILE to UPPER_SNAKE_CASE."""
    with open(env_file) as f:
        content = f.read()

    result = normalize_env(content)
    serialized = serialize_env(result.output)

    if output:
        with open(output, "w") as f:
            f.write(serialized)
        click.echo(f"Written to {output}")
    else:
        click.echo(serialized)

    if show_summary:
        click.echo(result.to_summary())

    if result.normalized_count > 0:
        for key in result.normalized:
            click.echo(f"  normalized: {key}", err=True)
