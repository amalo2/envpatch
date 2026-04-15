"""CLI command for scoring an .env file."""
import sys
import click

from envpatch.scorer import score_env


@click.command("score")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--min-score",
    default=0,
    show_default=True,
    type=int,
    help="Exit with code 1 if score is below this threshold.",
)
def score_cmd(env_file: str, output_format: str, min_score: int) -> None:
    """Score the quality of an .env file (0-100)."""
    with open(env_file, "r") as fh:
        content = fh.read()

    result = score_env(content)

    if output_format == "json":
        import json

        data = {
            "score": result.score,
            "grade": result.grade,
            "total_keys": result.total_keys,
            "penalties": result.penalties,
        }
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(result.to_summary())

    if result.score < min_score:
        click.echo(
            f"Score {result.score} is below minimum threshold {min_score}.",
            err=True,
        )
        sys.exit(1)
