import click
from envpatch.grouper import group_env, filter_group


@click.command("group")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--delimiter", "-d", default="_", show_default=True, help="Key prefix delimiter.")
@click.option("--prefix", "-p", default=None, help="Show only keys for a specific prefix group.")
@click.option("--summary", "mode", flag_value="summary", default=True, help="Print group summary.")
@click.option("--list", "mode", flag_value="list", help="List all keys with their groups.")
def group_cmd(env_file, delimiter, prefix, mode):
    """Group env keys by prefix."""
    with open(env_file) as f:
        content = f.read()

    result = group_env(content, delimiter=delimiter)

    if prefix:
        keys = filter_group(result, prefix)
        if keys is None:
            click.echo(f"No group found for prefix: {prefix}", err=True)
            raise SystemExit(1)
        for k, v in keys.items():
            click.echo(f"{k}={v}")
        return

    if mode == "list":
        for group_name, keys in result.groups.items():
            for k, v in keys.items():
                click.echo(f"[{group_name}] {k}={v}")
        for k, v in result.ungrouped.items():
            click.echo(f"[ungrouped] {k}={v}")
    else:
        click.echo(result.to_summary())
