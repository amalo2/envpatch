import click
from envpatch.parser import parse_env_file
from envpatch.typecheck import typecheck_env


@click.command("typecheck")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--show-untyped", is_flag=True, default=False, help="List untyped keys")
@click.option("--fail-on-untyped", is_flag=True, default=False, help="Exit 1 if any untyped keys exist")
def typecheck_cmd(env_file: str, show_untyped: bool, fail_on_untyped: bool) -> None:
    """Detect value types for keys in an env file."""
    env = parse_env_file(env_file)
    result = typecheck_env(env)

    click.echo(f"Typed keys   : {result.typed_count}")
    click.echo(f"Untyped keys : {result.untyped_count}")

    for hint in result.hints:
        click.echo(f"  {hint.key} = {hint.value!r}  [{hint.detected}]")

    if show_untyped and result.untyped:
        click.echo("Untyped:")
        for key in result.untyped:
            click.echo(f"  {key}")

    if fail_on_untyped and result.untyped_count > 0:
        raise SystemExit(1)
