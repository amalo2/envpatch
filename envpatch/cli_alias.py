import click
from envpatch.parser import parse_env_file
from envpatch.aliaser import alias_keys
from envpatch.patcher import serialize_env


@click.command("alias")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--map",
    "mappings",
    multiple=True,
    required=True,
    metavar="SOURCE:ALIAS",
    help="Key alias mapping in SOURCE:ALIAS format. Repeatable.",
)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing alias keys.")
@click.option("--output", "-o", type=click.Path(), default=None, help="Write result to file.")
@click.option("--summary", is_flag=True, default=False, help="Print summary.")
def alias_cmd(env_file, mappings, overwrite, output, summary):
    """Create alias keys that mirror existing key values."""
    env = parse_env_file(env_file)

    aliases = {}
    for mapping in mappings:
        if ":" not in mapping:
            raise click.BadParameter(f"Invalid mapping '{mapping}', expected SOURCE:ALIAS")
        source, alias = mapping.split(":", 1)
        aliases[source.strip()] = alias.strip()

    result = alias_keys(env, aliases, overwrite=overwrite)
    serialized = serialize_env(result.env)

    if output:
        with open(output, "w") as f:
            f.write(serialized)
    else:
        click.echo(serialized)

    if summary:
        click.echo(result.to_summary(), err=True)
