import click
from envpatch.prefixer import prefix_env
from envpatch.patcher import serialize_env


@click.command("prefix")
@click.argument("env_file", type=click.Path(exists=True))
@click.argument("prefix")
@click.option("--strip", is_flag=True, default=False, help="Remove prefix instead of adding it.")
@click.option(
    "--no-skip",
    "skip_existing",
    is_flag=True,
    default=True,
    flag_value=False,
    help="Re-prefix keys that already start with PREFIX.",
)
@click.option("--output", "-o", type=click.Path(), default=None, help="Write result to file.")
@click.option("--summary", is_flag=True, default=False, help="Print summary after processing.")
def prefix_cmd(env_file, prefix, strip, skip_existing, output, summary):
    """Add or remove PREFIX from all keys in ENV_FILE."""
    with open(env_file) as fh:
        source = fh.read()

    result = prefix_env(source, prefix, skip_existing=skip_existing, strip=strip)
    serialized = serialize_env(result.env)

    if output:
        with open(output, "w") as fh:
            fh.write(serialized)
        click.echo(f"Written to {output}")
    else:
        click.echo(serialized, nl=False)

    if summary:
        click.echo(result.to_summary(), err=True)
