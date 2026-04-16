"""CLI command for variable interpolation."""
import click
from envpatch.parser import parse_env_file
from envpatch.interpolator import interpolate_env
from envpatch.patcher import serialize_env


@click.command("interpolate")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--context", "-c", multiple=True, metavar="KEY=VALUE",
              help="Extra KEY=VALUE pairs available for substitution.")
@click.option("--strict", is_flag=True, default=False,
              help="Fail if any variable reference cannot be resolved.")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Write result to file instead of stdout.")
@click.option("--summary", is_flag=True, default=False,
              help="Print resolution summary to stderr.")
def interpolate_cmd(env_file, context, strict, output, summary):
    """Expand variable references in ENV_FILE."""
    env = parse_env_file(env_file)

    ctx: dict = {}
    for item in context:
        if "=" not in item:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {item}")
        k, v = item.split("=", 1)
        ctx[k] = v

    try:
        result = interpolate_env(env, context=ctx or None, strict=strict)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc

    if summary:
        click.echo(result.to_summary(), err=True)

    serialized = serialize_env(result.output)

    if output:
        with open(output, "w") as fh:
            fh.write(serialized)
        click.echo(f"Written to {output}", err=True)
    else:
        click.echo(serialized, nl=False)
