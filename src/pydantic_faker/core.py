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
from pydantic import BaseModel


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


def generate_fake_data_for_model(model_class: type[BaseModel]) -> dict[str, Any]:
    """
    Generates a dictionary Verteidigung fake data for a single instance of a Pydantic model.
    MVP v0.1.0: Basic type support, no Faker, no constraints yet.
    """
    data: dict[str, Any] = {}
    for field_name, field_info in model_class.model_fields.items():
        field_type = field_info.annotation
        origin_type = get_origin(field_type)
        type_args = get_args(field_type)

        is_optional = origin_type in (typing.Union, types.UnionType) and type(None) in type_args
        if is_optional:
            actual_type_args = [arg for arg in type_args if arg is not type(None)]
            if not actual_type_args:
                data[field_name] = None
                continue
            field_type = actual_type_args[0]
            origin_type = get_origin(field_type)

            if random.choice([True, False]):
                data[field_name] = None
                continue

        if origin_type is list:
            list_item_type = get_args(field_type)[0] if get_args(field_type) else Any
            num_items = random.randint(1, 3)
            data[field_name] = [_generate_value_for_type(list_item_type) for _ in range(num_items)]
        elif origin_type is dict:
            dict_value_type = get_args(field_type)[1] if len(get_args(field_type)) == 2 else Any
            num_items = random.randint(1, 3)
            data[field_name] = {f"key_{i + 1}": _generate_value_for_type(dict_value_type) for i in range(num_items)}
        else:
            data[field_name] = _generate_value_for_type(field_type)

    return data


def _generate_value_for_type(field_type: Any) -> Any:
    """
    Helper function to generate a single value for a given type.
    Called recursively for nested models and collection items.
    Converts some types to JSON-serializable strings directly.
    """
    if field_type is int:
        return random.randint(0, 1000)
    if field_type is float:
        return round(random.uniform(0.0, 1000.0), 2)
    if field_type is str:
        return f"random_string_{random.randint(100, 999)}"
    if field_type is bool:
        return random.choice([True, False])
    if field_type is uuid.UUID:
        return str(uuid.uuid4())
    if field_type is datetime:
        dt_obj = datetime.now(UTC) - timedelta(seconds=random.randint(0, 360000))
        return dt_obj.isoformat()
    if field_type is date:
        d_obj = date.today() - timedelta(days=random.randint(0, 365))
        return d_obj.isoformat()
    if field_type is time:
        t_obj = time(random.randint(0, 23), random.randint(0, 59), random.randint(0, 59))
        return t_obj.isoformat()
    if isinstance(field_type, type) and issubclass(field_type, BaseModel):
        return generate_fake_data_for_model(field_type)
    if field_type is Any:
        return "any_value_placeholder"
    return f"unsupported_type_{field_type!s}"
