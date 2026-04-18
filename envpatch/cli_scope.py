import click
from envpatch.scoper import scope_env


@click.command("scope")
@click.argument("env_file", type=click.Path(exists=True))
@click.argument("scope")
@click.option("--prefix", multiple=True, help="Explicit prefix(es) to match (e.g. AWS_).")
@click.option("--strip-prefix", is_flag=True, default=False, help="Remove matched prefix from output keys.")
@click.option("--output", type=click.Path(), default=None, help="Write scoped env to file.")
def scope_cmd(env_file, scope, prefix, strip_prefix, output):
    """Filter ENV_FILE to keys matching SCOPE (or explicit prefixes)."""
    with open(env_file) as f:
        source = f.read()

    prefixes = list(prefix) if prefix else None
    result = scope_env(source, scope, prefixes=prefixes, strip_prefix=strip_prefix)

    lines = [f"{k}={v}" for k, v in result.env.items()]
    env_text = "\n".join(lines)

    if output:
        with open(output, "w") as f:
            f.write(env_text + "\n")
        click.echo(f"Wrote {result.included_count} keys to {output}")
    else:
        if env_text:
            click.echo(env_text)

    click.echo(result.to_summary(), err=True)
