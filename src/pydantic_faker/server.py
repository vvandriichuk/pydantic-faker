import random
import uuid
from typing import Any

import typer
import uvicorn
from faker import Faker
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .core import generate_fake_data_for_model, get_faker_instance, load_pydantic_model

IN_MEMORY_DATA: dict[str, list[dict[str, Any]]] = {}


def create_fastapi_app(
    model_class: type[BaseModel],
    data_instances: list[dict[str, Any]],
) -> FastAPI:
    app = FastAPI(
        title=f"Pydantic-Faker Mock API for {model_class.__name__}",
        version="0.3.0",
    )

    resource_name = model_class.__name__.lower()
    if not resource_name.endswith("s"):
        resource_name += "s"

    IN_MEMORY_DATA[resource_name] = data_instances

    @app.get(f"/{resource_name}", response_model=list[model_class])  # type: ignore[valid-type]
    async def get_all_items() -> list[dict[str, Any]]:
        return IN_MEMORY_DATA.get(resource_name, [])

    @app.get(f"/{resource_name}/{{item_id_str}}", response_model=model_class)  # type: ignore[valid-type]
    async def get_item(item_id_str: str) -> dict[str, Any]:
        items = IN_MEMORY_DATA.get(resource_name, [])

        id_field_name: str | None = None
        id_field_type: type | None = None

        if "id" in model_class.model_fields:
            id_field_name = "id"
            id_field_type = model_class.model_fields["id"].annotation
        elif "uuid" in model_class.model_fields:
            id_field_name = "uuid"
            id_field_type = model_class.model_fields["uuid"].annotation

        found_item = None
        if id_field_name and id_field_type:
            for item in items:
                model_id_value = item.get(id_field_name)
                if model_id_value is None:
                    continue

                try:
                    if id_field_type is int:
                        if int(model_id_value) == int(item_id_str):
                            found_item = item
                            break
                    elif id_field_type is uuid.UUID:
                        if str(model_id_value) == item_id_str:
                            found_item = item
                            break
                    else:
                        if str(model_id_value) == item_id_str:
                            found_item = item
                            break
                except (ValueError, TypeError):
                    pass

        if found_item:
            return found_item

        try:
            index = int(item_id_str)
            if 0 <= index < len(items):
                return items[index]
        except ValueError:
            pass

        raise HTTPException(status_code=404, detail=f"{model_class.__name__} with id/index '{item_id_str}' not found.")

    return app


def run_server(
    model_path_str: str,
    count: int,
    faker_locale: str | None,
    seed: int | None,
    host: str,
    port: int,
) -> None:
    try:
        model_class = load_pydantic_model(model_path_str)
    except typer.Exit:
        return

    faker_for_server: Faker | None = None
    if seed is not None:
        random.seed(seed)
        faker_for_server = get_faker_instance(locale=faker_locale, seed=seed)

    data_instances: list[dict[str, Any]] = []
    for _ in range(count):
        effective_faker_instance = faker_for_server if faker_for_server else get_faker_instance(locale=faker_locale)

        try:
            single_instance = generate_fake_data_for_model(
                model_class=model_class,
                faker_instance_override=effective_faker_instance,
            )
            data_instances.append(single_instance)
        except Exception as e:
            print(f"❌ Error during data generation for an instance of {model_class.__name__}: {e}")
            return

    if not data_instances:
        print("❌ No data instances were generated. Server cannot start.")
        return

    app_instance = create_fastapi_app(model_class, data_instances)

    print(f"Running Uvicorn on http://{host}:{port}")
    uvicorn.run(
        app_instance,
        host=host,
        port=port,
        log_level="info",
    )
