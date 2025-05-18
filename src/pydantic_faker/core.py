import importlib
import random
import sys
import types
import typing
import uuid
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any, get_args, get_origin

import typer
from faker import Faker
from pydantic import BaseModel


def get_faker_instance(locale: str | None = None, seed: int | None = None) -> Faker:
    """Creates or reuses a Faker instance with a specific locale and seed."""
    faker_instance = Faker(locale=locale)
    if seed is not None:
        Faker.seed(seed)
        faker_instance.seed_instance(seed)
    return faker_instance


def load_pydantic_model(model_path_str: str) -> type[BaseModel]:
    """
    Loads a Pydantic model class from a string path like "module:ClassName".
    Adds the current working directory to sys.path to find local modules.
    """
    current_working_directory = str(Path.cwd())
    if current_working_directory not in sys.path:
        sys.path.insert(0, current_working_directory)

    try:
        module_str, class_name_str = model_path_str.rsplit(":", 1)
    except ValueError as ve:
        error_message = (
            f"❌ Invalid model path format: '{model_path_str}'. "
            "Expected 'module:ClassName' or 'package.module:ClassName'."
        )
        typer.secho(
            error_message,
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1) from ve

    try:
        module = importlib.import_module(module_str)
    except ImportError as e:
        error_message = f"❌ Error importing module '{module_str}': {e}"
        typer.secho(
            error_message,
            fg=typer.colors.RED,
            err=True,
        )
        typer.echo("💡 Make sure the module is in your Python path or current working directory.")
        raise typer.Exit(code=1) from e

    try:
        model_class = getattr(module, class_name_str)
    except AttributeError as ae:
        error_message = f"❌ Class '{class_name_str}' not found in module '{module_str}'."
        typer.secho(
            error_message,
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1) from ae

    if not isinstance(model_class, type) or not issubclass(model_class, BaseModel):
        typer.secho(
            f"❌ '{model_path_str}' is not a Pydantic BaseModel subclass.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    return model_class


def generate_fake_data_for_model(
    model_class: type[BaseModel],
    faker_locale: str | None = None,
    seed: int | None = None,
    faker_instance_override: Faker | None = None,
) -> dict[str, Any]:
    """
    Generates a dictionary with fake data for a single instance of a Pydantic model.
    Handles Faker integration by field name, considering locale and seed.
    """
    current_faker_instance: Faker  # Объявляем тип

    if faker_instance_override:
        current_faker_instance = faker_instance_override
    else:
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)

        current_faker_instance = Faker(locale=faker_locale)
        if seed is not None:
            current_faker_instance.seed_instance(seed)

    FAKER_FIELD_NAME_MAP = {
        "name": lambda: current_faker_instance.name(),
        "first_name": lambda: current_faker_instance.first_name(),
        "last_name": lambda: current_faker_instance.last_name(),
        "user_name": lambda: current_faker_instance.user_name(),
        "username": lambda: current_faker_instance.user_name(),
        "email": lambda: current_faker_instance.email(),
        "address": lambda: current_faker_instance.address(),
        "phone_number": lambda: current_faker_instance.phone_number(),
        "company": lambda: current_faker_instance.company(),
        "job": lambda: current_faker_instance.job(),
        "text": lambda: current_faker_instance.text(max_nb_chars=150),
        "sentence": lambda: current_faker_instance.sentence(),
        "paragraph": lambda: current_faker_instance.paragraph(),
        "url": lambda: current_faker_instance.url(),
        "uri": lambda: current_faker_instance.uri(),
        "ipv4": lambda: current_faker_instance.ipv4_public(),
        "color_name": lambda: current_faker_instance.color_name(),
        "hex_color": lambda: current_faker_instance.hex_color(),
        "country": lambda: current_faker_instance.country(),
        "city": lambda: current_faker_instance.city(),
        "zip_code": lambda: current_faker_instance.zipcode(),
    }

    data: dict[str, Any] = {}
    for field_name, field_info in model_class.model_fields.items():
        current_field_annotation = field_info.annotation
        origin_type = get_origin(current_field_annotation)
        type_args = get_args(current_field_annotation)
        is_optional = origin_type in (typing.Union, types.UnionType) and type(None) in type_args

        field_type_for_generation: Any

        if is_optional:
            if random.choice([True, False]):
                data[field_name] = None
                continue

            actual_type_args = [arg for arg in type_args if arg is not type(None)]
            if not actual_type_args:
                data[field_name] = None
                continue
            field_type_for_generation = actual_type_args[0]
        else:
            field_type_for_generation = current_field_annotation

        if field_name in FAKER_FIELD_NAME_MAP:
            data[field_name] = FAKER_FIELD_NAME_MAP[field_name]()
            continue

        current_origin_for_generation = get_origin(field_type_for_generation)

        if current_origin_for_generation is list:
            list_item_type_args = get_args(field_type_for_generation)
            list_item_type = list_item_type_args[0] if list_item_type_args else Any
            num_items = random.randint(1, 3)
            data[field_name] = [
                _generate_value_for_type(list_item_type, current_faker_instance) for _ in range(num_items)
            ]
        elif current_origin_for_generation is dict:
            dict_type_args = get_args(field_type_for_generation)
            dict_value_type = dict_type_args[1] if len(dict_type_args) == 2 else Any
            num_items = random.randint(1, 3)
            data[field_name] = {
                current_faker_instance.word(): _generate_value_for_type(dict_value_type, current_faker_instance)
                for _ in range(num_items)
            }
        else:
            data[field_name] = _generate_value_for_type(field_type_for_generation, current_faker_instance)

    return data


def _generate_value_for_type(field_type_to_generate: Any, faker_instance: Faker) -> Any:
    """
    Helper function to generate a single value for a given *basic* type
    or recursively call for nested Pydantic models.
    Uses the provided Faker instance for string generation.
    """
    if field_type_to_generate is int:
        return random.randint(0, 1000)
    if field_type_to_generate is float:
        return round(random.uniform(0.0, 1000.0), 2)
    if field_type_to_generate is str:
        return faker_instance.sentence(nb_words=3)
    if field_type_to_generate is bool:
        return random.choice([True, False])
    if field_type_to_generate is uuid.UUID:
        return faker_instance.uuid4(cast_to=str)
    if field_type_to_generate is datetime:
        start_date = "-10y"
        dt_obj = faker_instance.date_time_between(start_date=start_date, end_date="now", tzinfo=UTC)
        return dt_obj.isoformat()
    if field_type_to_generate is date:
        d_obj = date.today() - timedelta(days=random.randint(0, 365))
        return d_obj.isoformat()
    if field_type_to_generate is time:
        t_obj = time(random.randint(0, 23), random.randint(0, 59), random.randint(0, 59))
        return t_obj.isoformat()
    if isinstance(field_type_to_generate, type) and issubclass(field_type_to_generate, BaseModel):
        return generate_fake_data_for_model(field_type_to_generate, faker_instance_override=faker_instance)
    if field_type_to_generate is Any:
        return "any_value_placeholder"

    return f"unsupported_type_{field_type_to_generate!s}"
