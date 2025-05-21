import json
from pathlib import Path
from typing import Annotated

import typer

from .core import generate_fake_data_for_model, load_pydantic_model
from .server import run_server

app = typer.Typer(
    name="pydantic-faker",
    help="🚀 A CLI tool to generate fake data from Pydantic models.",
    add_completion=True,
    no_args_is_help=True,
)


@app.command()
def generate(
    model_path: Annotated[
        str,
        typer.Argument(
            help="Path to the Pydantic model, e.g., 'my_module:MyModel' or 'my_module.sub_module:MyModel'.",
        ),
    ],
    count: Annotated[
        int,
        typer.Option(
            "--count",
            "-c",
            help="Number of fake data instances to generate.",
            min=1,
            show_default=True,
        ),
    ] = 1,
    output_file: Annotated[
        Path | None,
        typer.Option(
            "--output-file",
            "-o",
            help="Path to save the generated JSON data. If not provided, prints to stdout.",
            writable=True,
            show_default=False,
        ),
    ] = None,
    faker_locale: Annotated[
        str | None,
        typer.Option(
            "--faker-locale",
            "-l",
            help="Locale to use for Faker (e.g., 'en_US', 'ru_RU', 'ja_JP'). If not provided, Faker's default is used.",
            show_default=False,
        ),
    ] = None,
    seed: Annotated[
        int | None,
        typer.Option(
            "--seed",
            "-s",
            help="Seed for the random number generator (for reproducible results).",
            show_default=False,
        ),
    ] = None,
) -> None:
    """
    Generates fake data based on a Pydantic model and outputs it as JSON.
    """
    typer.echo(f"⏳ Generating {count} instance(s) for model: {model_path}")
    if faker_locale:
        typer.echo(f"🌍 Using Faker locale: {faker_locale}")
    if seed is not None:
        typer.echo(f"🌱 Using random seed: {seed}")

    try:
        pydantic_model_class = load_pydantic_model(model_path)
        typer.echo(f"🔍 Successfully loaded model: {pydantic_model_class.__name__}")
    except typer.Exit:
        raise

    fake_data_list = []
    for _ in range(count):
        try:
            single_fake_data = generate_fake_data_for_model(
                model_class=pydantic_model_class,
                faker_locale=faker_locale,
                seed=seed,
            )
            fake_data_list.append(single_fake_data)
        except Exception as e:
            typer.secho(
                f"❌ Error generating data for model {pydantic_model_class.__name__}: {e}",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=1) from e

    if output_file:
        try:
            with output_file.open("w", encoding="utf-8") as f:
                json.dump(fake_data_list, f, indent=2, ensure_ascii=False)
            typer.secho(f"✅ Data successfully saved to: {output_file}", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"❌ Error saving data to file: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1) from e
    else:
        typer.echo(json.dumps(fake_data_list, indent=2, ensure_ascii=False))

    typer.echo("🎉 Generation complete!")


@app.command()
def serve(
    model_path: Annotated[
        str,
        typer.Argument(help="Path to the Pydantic model, e.g., 'my_module:MyModel'."),
    ],
    count: Annotated[
        int,
        typer.Option("--count", "-c", help="Number of fake data instances per model.", min=1, show_default=True),
    ] = 10,
    faker_locale: Annotated[
        str | None,
        typer.Option("--faker-locale", "-l", help="Locale for Faker.", show_default=False),
    ] = None,
    seed: Annotated[
        int | None,
        typer.Option("--seed", "-s", help="Random seed for reproducibility.", show_default=False),
    ] = None,
    host: Annotated[
        str,
        typer.Option(help="Host to bind the server to."),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option(help="Port to run the server on."),
    ] = 8000,
) -> None:
    """
    Generates fake data and serves it via a local HTTP mock API.
    """
    typer.secho(f"🚀 Starting mock API server for model at: {model_path}", fg=typer.colors.CYAN)
    typer.echo(f"   Serving {count} fake instance(s).")
    if faker_locale:
        typer.echo(f"   🌍 Using Faker locale: {faker_locale}")
    if seed is not None:
        typer.echo(f"   🌱 Using random seed: {seed}")

    run_server(
        model_path_str=model_path,
        count=count,
        faker_locale=faker_locale,
        seed=seed,
        host=host,
        port=port,
    )
