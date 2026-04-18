import click
from envpatch.pinner import pin_env, serialize_pinned


@click.command("pin")
@click.argument("env_file", type=click.Path(exists=True))
@click.argument("keys", nargs=-1, required=True)
@click.option("--marker", default="# pinned", show_default=True, help="Inline comment marker to append.")
@click.option("--overwrite", is_flag=True, default=False, help="Re-pin already-pinned keys.")
@click.option("--write", is_flag=True, default=False, help="Write changes back to the file.")
@click.option("--summary", "show_summary", is_flag=True, default=False, help="Print summary only.")
def pin_cmd(env_file, keys, marker, overwrite, write, show_summary):
    """Pin specific keys in an .env file by appending a marker comment."""
    with open(env_file) as f:
        content = f.read()

    key_list = list(keys)
    result = pin_env(content, key_list, marker=marker, overwrite=overwrite)

    if show_summary:
        click.echo(result.to_summary())
        return

    output = serialize_pinned(content, key_list, marker=marker)

    if write:
        with open(env_file, "w") as f:
            f.write(output)
        click.echo(f"Written to {env_file}")
    else:
        click.echo(output)

    click.echo(result.to_summary())
