import random
import uuid
from types import UnionType
from typing import Any, Union, get_args, get_origin

import typer
import uvicorn
from faker import Faker
from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel

from .core import generate_fake_data_for_model, get_faker_instance, load_pydantic_model

IN_MEMORY_DATA: dict[str, list[dict[str, Any]]] = {}


def _get_next_id(items: list[dict[str, Any]], id_field_name: str = "id") -> int:
    """Generates the next ID based on the existing ones if it is int."""
    if not items:
        return 1
    max_id = 0
    for item in items:
        item_id_val = item.get(id_field_name)
        if isinstance(item_id_val, int) and item_id_val > max_id:
            max_id = item_id_val
    return max_id + 1


def create_fastapi_app(
    model_class: type[BaseModel],
    data_instances: list[dict[str, Any]],
    faker_instance_for_new_items: Faker,
) -> FastAPI:
    app = FastAPI(
        title=f"Pydantic-Faker Mock API for {model_class.__name__}",
        version="0.4.0",
    )

    resource_name = model_class.__name__.lower()
    if not resource_name.endswith("s"):
        resource_name += "s"

    # Initialize the storage for this model if it doesn't exist yet
    IN_MEMORY_DATA.setdefault(resource_name, []).clear()  # Clean before filling
    IN_MEMORY_DATA[resource_name].extend(data_instances)

    @app.get(f"/{resource_name}", response_model=list[model_class])  # type: ignore[valid-type]
    async def get_all_items(request: Request) -> list[dict[str, Any]]:
        all_items = IN_MEMORY_DATA.get(resource_name, [])
        query_params = request.query_params

        if not query_params:
            return all_items

        final_filtered_items: list[dict[str, Any]] = []

        for item in all_items:
            current_item_matches_all_query_filters = True
            for query_field_name, query_value_str in query_params.items():
                if query_field_name not in model_class.model_fields:
                    continue

                model_field = model_class.model_fields[query_field_name]
                item_value = item.get(query_field_name)

                original_annotation = model_field.annotation
                origin = get_origin(original_annotation)
                type_for_comparison = original_annotation

                if origin in (Union, UnionType):
                    args = get_args(original_annotation)
                    non_none_args = [arg for arg in args if arg is not type(None)]
                    if len(non_none_args) == 1 and type(None) in args:
                        type_for_comparison = non_none_args[0]
                    elif not non_none_args and type(None) in args:
                        type_for_comparison = type(None)

                param_match_for_item = False
                try:
                    if item_value is None:
                        if query_value_str.lower() == "none" or query_value_str == "":
                            param_match_for_item = True
                    elif type_for_comparison is bool:
                        query_bool = None
                        if query_value_str.lower() in ("true", "1", "yes", "on"):
                            query_bool = True
                        elif query_value_str.lower() in ("false", "0", "no", "off"):
                            query_bool = False
                        if query_bool is not None and item_value == query_bool:
                            param_match_for_item = True
                    elif type_for_comparison is int:
                        if int(item_value) == int(query_value_str):
                            param_match_for_item = True
                    elif type_for_comparison is float:
                        if abs(float(item_value) - float(query_value_str)) < 1e-9:
                            param_match_for_item = True
                    elif type_for_comparison is uuid.UUID:
                        if str(item_value) == query_value_str:
                            param_match_for_item = True
                    else:
                        if str(item_value) == query_value_str:
                            param_match_for_item = True
                except (ValueError, TypeError):
                    param_match_for_item = False

                if not param_match_for_item:
                    current_item_matches_all_query_filters = False
                    break

            if current_item_matches_all_query_filters:
                final_filtered_items.append(item)

        return final_filtered_items

    @app.get(f"/{resource_name}/{{item_id_str}}", response_model=model_class)  # type: ignore[valid-type]
    async def get_item(item_id_str: str) -> dict[str, Any]:
        items = IN_MEMORY_DATA.get(resource_name, [])
        id_field_name: str | None = None

        if "id" in model_class.model_fields:
            id_field_name = "id"
        elif "uuid" in model_class.model_fields:
            id_field_name = "uuid"

        found_item = None
        if id_field_name:
            for item in items:
                model_id_value = item.get(id_field_name)
                if model_id_value is None:
                    continue
                if str(model_id_value) == item_id_str:
                    found_item = item
                    break

        if found_item:
            return found_item

        try:
            index = int(item_id_str)
            if 0 <= index < len(items):
                return items[index]
        except ValueError:
            pass

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model_class.__name__} with id/index '{item_id_str}' not found.",
        )

    @app.post(f"/{resource_name}", response_model=model_class, status_code=status.HTTP_201_CREATED)  # type: ignore[valid-type]
    async def create_item(item_payload: model_class) -> dict[str, Any]:  # type: ignore[valid-type]
        items = IN_MEMORY_DATA.setdefault(resource_name, [])
        item_dict = item_payload.model_dump()  # type: ignore[attr-defined]

        # Simple logic for ID: if there is an 'id' (int) field and it is not passed, generate the following.
        # If 'uuid' (str), generate a new UUID.
        if "id" in model_class.model_fields and model_class.model_fields["id"].annotation is int:
            if item_dict.get("id") is None:  # Or if the ID is not required and not passed
                item_dict["id"] = _get_next_id(items, "id")
            elif (
                "uuid" in model_class.model_fields
                and model_class.model_fields["uuid"].annotation is uuid.UUID
                and item_dict.get("uuid") is None
            ):
                item_dict["uuid"] = str(faker_instance_for_new_items.uuid4())

        items.append(item_dict)
        return item_dict  # type: ignore[no-any-return]

    @app.put(f"/{resource_name}/{{item_id_str}}", response_model=model_class)  # type: ignore[valid-type]
    async def update_item(item_id_str: str, item_payload: model_class) -> dict[str, Any]:  # type: ignore[valid-type]
        items = IN_MEMORY_DATA.get(resource_name, [])
        id_field_name: str | None = None
        if "id" in model_class.model_fields:
            id_field_name = "id"
        elif "uuid" in model_class.model_fields:
            id_field_name = "uuid"

        item_to_update_index: int | None = None
        if id_field_name:
            for i, current_item in enumerate(items):
                if str(current_item.get(id_field_name)) == item_id_str:
                    item_to_update_index = i
                    break

        if item_to_update_index is None:  # If you didn't find it by ID, try by index
            try:
                index = int(item_id_str)
                if 0 <= index < len(items):
                    item_to_update_index = index
            except ValueError:
                pass

        if item_to_update_index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item '{item_id_str}' not found to update.",
            )

        updated_item_dict = item_payload.model_dump()  # type: ignore[attr-defined]
        # Make sure the ID doesn't change when updating (or that the ID from the path matches the ID in the payload)
        if id_field_name and items[item_to_update_index].get(id_field_name) is not None:
            updated_item_dict[id_field_name] = items[item_to_update_index][id_field_name]

        items[item_to_update_index] = updated_item_dict
        return updated_item_dict  # type: ignore[no-any-return]

    @app.delete(f"/{resource_name}/{{item_id_str}}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_item(item_id_str: str) -> None:
        items = IN_MEMORY_DATA.get(resource_name, [])
        id_field_name: str | None = None
        if "id" in model_class.model_fields:
            id_field_name = "id"
        elif "uuid" in model_class.model_fields:
            id_field_name = "uuid"

        item_to_delete_index: int | None = None
        if id_field_name:
            for i, current_item in enumerate(items):
                if str(current_item.get(id_field_name)) == item_id_str:
                    item_to_delete_index = i
                    break

        if item_to_delete_index is None:  # Если не нашли по ID, пробуем по индексу
            try:
                index = int(item_id_str)
                if 0 <= index < len(items):
                    item_to_delete_index = index
            except ValueError:
                pass

        if item_to_delete_index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item '{item_id_str}' not found to delete.",
            )

        items.pop(item_to_delete_index)
        return  # For 204 No Content FastAPI will return an empty response.

    print(f"   POST http://<host>:<port>/{resource_name}")
    print(f"   PUT http://<host>:<port>/{resource_name}/<id_or_index>")
    print(f"   DELETE http://<host>:<port>/{resource_name}/<id_or_index>")
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

    main_faker_instance = get_faker_instance(locale=faker_locale, seed=seed)
    if seed is not None:
        random.seed(seed)

    data_instances: list[dict[str, Any]] = []
    for _ in range(count):
        try:
            single_instance = generate_fake_data_for_model(
                model_class=model_class,
                faker_instance_override=main_faker_instance,
            )
            data_instances.append(single_instance)
        except Exception as e:
            print(f"❌ Error during data generation: {e}")
            return

    if not data_instances:
        print("❌ No data instances generated. Server cannot start.")
        return

    app_instance = create_fastapi_app(model_class, data_instances, main_faker_instance)

    print(f"Running Uvicorn on http://{host}:{port}")
    uvicorn.run(
        app_instance,
        host=host,
        port=port,
        log_level="info",
    )
