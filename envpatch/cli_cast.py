import click
import json
from envpatch.parser import parse_env_file
from envpatch.caster import cast_env


@click.command("cast")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--keys", "-k", multiple=True, help="Specific keys to cast (default: all)")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
def cast_cmd(env_file: str, keys: tuple, fmt: str) -> None:
    """Cast .env values to native types and display results."""
    env = parse_env_file(env_file)
    selected = list(keys) if keys else None
    result = cast_env(env, keys=selected)

    if fmt == "json":
        output = {
            k: v if not isinstance(v, list) else v
            for k, v in result.cast.items()
        }
        click.echo(json.dumps(output, indent=2))
    else:
        click.echo(result.to_summary())
        for key, value in result.cast.items():
            type_name = type(value).__name__
            click.echo(f"  {key} = {value!r}  ({type_name})")
        if result.failed:
            click.echo(f"\nFailed keys: {', '.join(result.failed)}")
