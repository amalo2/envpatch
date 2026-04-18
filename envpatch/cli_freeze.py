import click
from envpatch.freezer import freeze_env


@click.command("freeze")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--key", "-k",
    multiple=True,
    help="Key(s) to freeze. If omitted, all keys are frozen.",
)
@click.option(
    "--marker",
    default="# frozen",
    show_default=True,
    help="Comment marker appended to frozen lines.",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    help="Write result to file instead of stdout.",
)
def freeze_cmd(env_file, key, marker, output):
    """Freeze env keys by appending a marker comment."""
    with open(env_file) as f:
        content = f.read()

    keys = list(key) if key else None
    result = freeze_env(content, keys=keys, marker=marker)
    out_content = result.frozen.get("__output__", content)

    if output:
        with open(output, "w") as f:
            f.write(out_content)
        click.echo(result.to_summary())
    else:
        click.echo(out_content)
        click.echo(result.to_summary(), err=True)
