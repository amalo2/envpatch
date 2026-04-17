import click
from envpatch.parser import parse_env_file
from envpatch.flattener import flatten_env
from envpatch.patcher import serialize_env


@click.command("flatten")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--prefix", default="", help="Only promote keys matching this prefix.")
@click.option("--separator", default="__", show_default=True, help="Segment separator.")
@click.option("--no-uppercase", is_flag=True, default=False, help="Preserve original case.")
@click.option("--output", "-o", type=click.Path(), default=None, help="Write result to file.")
@click.option("--summary", is_flag=True, default=False, help="Print summary only.")
def flatten_cmd(env_file, prefix, separator, no_uppercase, output, summary):
    """Flatten namespaced env keys by stripping a prefix segment."""
    env = parse_env_file(env_file)
    result = flatten_env(
        env,
        prefix=prefix,
        separator=separator,
        uppercase=not no_uppercase,
    )

    if summary:
        click.echo(result.to_summary())
        return

    serialised = serialize_env(result.flattened)

    if output:
        with open(output, "w") as f:
            f.write(serialised)
        click.echo(f"Written to {output}")
        click.echo(result.to_summary())
    else:
        click.echo(serialised)
        click.echo(result.to_summary(), err=True)
