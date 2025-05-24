import importlib
import random
import sys
import uuid
from datetime import UTC, date, datetime, time
from enum import Enum
from pathlib import Path
from types import UnionType
from typing import Any, Literal, Union, get_args, get_origin

import typer
from faker import Faker
from pydantic import BaseModel


def get_faker_instance(locale: str | None = None, seed: int | None = None) -> Faker:
    """Creates a Faker instance with a specific locale and seed."""
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
        typer.secho(error_message, fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from ve

    try:
        module = importlib.import_module(module_str)
    except ImportError as e:
        error_message = f"❌ Error importing module '{module_str}': {e}"
        typer.secho(error_message, fg=typer.colors.RED, err=True)
        typer.echo("💡 Make sure the module is in your Python path or current working directory.")
        raise typer.Exit(code=1) from e

    try:
        model_class = getattr(module, class_name_str)
    except AttributeError as ae:
        error_message = f"❌ Class '{class_name_str}' not found in module '{module_str}'."
        typer.secho(error_message, fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from ae

    if not isinstance(model_class, type) or not issubclass(model_class, BaseModel):
        typer.secho(f"❌ '{model_path_str}' is not a Pydantic BaseModel subclass.", fg=typer.colors.RED, err=True)
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
    Applies Pydantic Field constraints.
    """
    current_faker_instance: Faker
    if faker_instance_override:
        current_faker_instance = faker_instance_override
    else:
        if seed is not None:
            random.seed(seed)
        current_faker_instance = get_faker_instance(locale=faker_locale, seed=seed)

    FAKER_FIELD_NAME_MAP = {
        "name": lambda: current_faker_instance.name(),
        "first_name": lambda: current_faker_instance.first_name(),
        "last_name": lambda: current_faker_instance.last_name(),
        "prefix": lambda: current_faker_instance.prefix(),  # e.g., Mr., Ms.
        "suffix": lambda: current_faker_instance.suffix(),  # e.g., Jr., MD
        "user_name": lambda: current_faker_instance.user_name(),
        "username": lambda: current_faker_instance.user_name(),
        "password": lambda: current_faker_instance.password(
            length=12,
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True,
        ),
        "email": lambda: current_faker_instance.email(),
        "safe_email": lambda: current_faker_instance.safe_email(),  # example.org, example.com, example.net
        "free_email": lambda: current_faker_instance.free_email(),  # gmail.com, hotmail.com
        "company_email": lambda: current_faker_instance.company_email(),
        "website": lambda: current_faker_instance.url(),
        "phone_number": lambda: current_faker_instance.phone_number(),
        # Адреса
        "address": lambda: current_faker_instance.address(),
        "street_address": lambda: current_faker_instance.street_address(),
        "secondary_address": lambda: current_faker_instance.secondary_address(),  # Apt. 123, Suite 456
        "building_number": lambda: current_faker_instance.building_number(),
        "street_name": lambda: current_faker_instance.street_name(),
        "city": lambda: current_faker_instance.city(),
        "state": lambda: current_faker_instance.state(),
        "zip_code": lambda: current_faker_instance.zipcode(),
        "postcode": lambda: current_faker_instance.postcode(),
        "country": lambda: current_faker_instance.country(),
        "country_code": lambda: current_faker_instance.country_code(),  # 'US', 'GB'
        "latitude": lambda: float(current_faker_instance.latitude()),
        "longitude": lambda: float(current_faker_instance.longitude()),
        "company": lambda: current_faker_instance.company(),
        "company_suffix": lambda: current_faker_instance.company_suffix(),  # Inc, LLC
        "catch_phrase": lambda: current_faker_instance.catch_phrase(),
        "bs": lambda: current_faker_instance.bs(),  # Corporate BS
        "job": lambda: current_faker_instance.job(),
        "text": lambda: current_faker_instance.text(max_nb_chars=200),
        "sentence": lambda: current_faker_instance.sentence(nb_words=6),
        "paragraph": lambda: current_faker_instance.paragraph(nb_sentences=3),
        "word": lambda: current_faker_instance.word(),
        "words": lambda: current_faker_instance.words(nb=3),
        "slug": lambda: current_faker_instance.slug(),
        "url": lambda: current_faker_instance.url(),
        "uri": lambda: current_faker_instance.uri(),
        "domain_name": lambda: current_faker_instance.domain_name(),
        "ipv4_private": lambda: current_faker_instance.ipv4_private(),
        "ipv4_public": lambda: current_faker_instance.ipv4_public(),
        "ipv4": lambda: current_faker_instance.ipv4(),
        "ipv6": lambda: current_faker_instance.ipv6(),
        "mac_address": lambda: current_faker_instance.mac_address(),
        "date": lambda: current_faker_instance.date(),
        "time": lambda: current_faker_instance.time(),
        "date_time": lambda: current_faker_instance.iso8601(),
        "iso8601": lambda: current_faker_instance.iso8601(),
        "timezone": lambda: current_faker_instance.timezone(),
        "color_name": lambda: current_faker_instance.color_name(),
        "hex_color": lambda: current_faker_instance.hex_color(),
        "rgb_color": lambda: current_faker_instance.rgb_color(),
        "safe_hex_color": lambda: current_faker_instance.safe_hex_color(),
        "file_name": lambda: current_faker_instance.file_name(),
        "file_extension": lambda: current_faker_instance.file_extension(),
        "mime_type": lambda: current_faker_instance.mime_type(),
        "boolean": lambda: current_faker_instance.boolean(chance_of_getting_true=50),
        "uuid4": lambda: current_faker_instance.uuid4(),
        "md5": lambda: current_faker_instance.md5(),
        "sha1": lambda: current_faker_instance.sha1(),
        "sha256": lambda: current_faker_instance.sha256(),
        "locale": lambda: current_faker_instance.locale(),
        "currency_code": lambda: current_faker_instance.currency_code(),
        "credit_card_number": lambda: current_faker_instance.credit_card_number(),
        "credit_card_expire": lambda: current_faker_instance.credit_card_expire(),
        "credit_card_security_code": lambda: current_faker_instance.credit_card_security_code(),
    }

    data: dict[str, Any] = {}
    for field_name, field_info in model_class.model_fields.items():
        current_field_annotation = field_info.annotation
        origin_type = get_origin(current_field_annotation)
        type_args = get_args(current_field_annotation)
        is_optional = origin_type in (Union, UnionType) and type(None) in type_args

        field_type_for_generation: Any

        if is_optional:
            if random.random() < 0.5:
                data[field_name] = None
                continue

            actual_type_args = [arg for arg in type_args if arg is not type(None)]
            if not actual_type_args:
                data[field_name] = None
                continue
            field_type_for_generation = actual_type_args[0]
        else:
            field_type_for_generation = current_field_annotation

        field_examples = getattr(field_info, "examples", None)
        use_example_value = False
        chosen_example_value = None

        if field_examples and isinstance(field_examples, list) and len(field_examples) > 0 and random.random() < 0.3:
            chosen_example_value = random.choice(field_examples)
            use_example_value = True

        if use_example_value:
            data[field_name] = chosen_example_value
            continue

        if field_name in FAKER_FIELD_NAME_MAP:
            generated_value_by_name = FAKER_FIELD_NAME_MAP[field_name]()

            generated_value = generated_value_by_name

            if isinstance(generated_value_by_name, str) and field_type_for_generation is str:
                raw_min_len = getattr(field_info, "min_length", None)
                raw_max_len = getattr(field_info, "max_length", None)

                text_to_modify = generated_value_by_name

                if raw_max_len is not None:
                    if raw_max_len < 0:
                        raw_max_len = 0
                    if len(text_to_modify) > raw_max_len:
                        text_to_modify = text_to_modify[:raw_max_len]

                if raw_min_len is not None:
                    if raw_min_len < 0:
                        raw_min_len = 0
                    if len(text_to_modify) < raw_min_len:
                        padding_needed = raw_min_len - len(text_to_modify)
                        if padding_needed > 0:
                            padding_chars = "".join(current_faker_instance.random_letters(length=padding_needed))
                            text_to_modify = text_to_modify + padding_chars

                            if raw_max_len is not None and len(text_to_modify) > raw_max_len:
                                text_to_modify = text_to_modify[:raw_max_len]

                generated_value = text_to_modify

            data[field_name] = generated_value
            continue

        current_origin_for_generation = get_origin(field_type_for_generation)

        if current_origin_for_generation is list:
            list_item_type_args = get_args(field_type_for_generation)
            list_item_type = list_item_type_args[0] if list_item_type_args else Any

            min_items = 1
            max_items = 3

            if hasattr(field_info, "metadata"):
                for constraint_obj in field_info.metadata:
                    if hasattr(constraint_obj, "min_length") and constraint_obj.min_length is not None:
                        min_items = constraint_obj.min_length
                    if hasattr(constraint_obj, "max_length") and constraint_obj.max_length is not None:
                        max_items = constraint_obj.max_length

            if min_items < 0:
                min_items = 0
            if max_items < 0:
                max_items = 0
            if min_items > max_items:
                max_items = min_items

            num_items = random.randint(min_items, max_items)
            data[field_name] = [
                _generate_value_for_type(list_item_type, current_faker_instance, None) for _ in range(num_items)
            ]
        elif current_origin_for_generation is dict:
            dict_type_args = get_args(field_type_for_generation)
            dict_value_type = dict_type_args[1] if len(dict_type_args) == 2 else Any

            min_items_dict = getattr(field_info, "min_length", 1)
            max_items_dict = getattr(field_info, "max_length", 3)
            if min_items_dict is None:
                min_items_dict = 1
            if max_items_dict is None:
                max_items_dict = 3
            if min_items_dict < 0:
                min_items_dict = 0
            if max_items_dict < 0:
                max_items_dict = 0
            if min_items_dict > max_items_dict:
                min_items_dict = max_items_dict

            num_items = random.randint(min_items_dict, max_items_dict)
            data[field_name] = {
                current_faker_instance.word(): _generate_value_for_type(
                    dict_value_type,
                    current_faker_instance,
                    None,
                )
                for _ in range(num_items)
            }
        else:
            data[field_name] = _generate_value_for_type(
                field_type_for_generation,
                current_faker_instance,
                field_info,
                field_name,
            )

    return data


def _generate_value_for_type(
    field_type_to_generate: Any,
    faker_instance: Faker,
    field_info: Any | None = None,
    field_name_for_debug: str = "unknown_field",
) -> Any:
    """
    Helper function to generate a single value for a given *basic* type
    or recursively call for nested Pydantic models.
    Uses field_info to apply constraints if available.
    """
    origin = get_origin(field_type_to_generate)
    args = get_args(field_type_to_generate)

    if origin is Literal:  # typing.Literal
        if args:
            return random.choice(args)
        return f"unsupported_type_empty_literal_{field_type_to_generate!s}"

    if isinstance(field_type_to_generate, type) and issubclass(field_type_to_generate, Enum):
        enum_members = list(field_type_to_generate)
        if enum_members:
            chosen_member = random.choice(enum_members)
            return chosen_member.value
        return f"unsupported_type_empty_enum_{field_type_to_generate.__name__}"

    if origin in (Union, UnionType):
        if args:
            chosen_type = random.choice(args)
            return _generate_value_for_type(chosen_type, faker_instance, None, f"{field_name_for_debug}_union_choice")
        return f"unsupported_type_empty_union_{field_type_to_generate!s}"

    gt_val, ge_val, lt_val, le_val, multiple_of_val = None, None, None, None, None
    min_length_val, max_length_val = None, None
    if field_info:
        min_length_val = getattr(field_info, "min_length", None)
        max_length_val = getattr(field_info, "max_length", None)
        gt_val = getattr(field_info, "gt", None)
        ge_val = getattr(field_info, "ge", None)
        lt_val = getattr(field_info, "lt", None)
        le_val = getattr(field_info, "le", None)
        multiple_of_val = getattr(field_info, "multiple_of", None)
        if hasattr(field_info, "metadata"):
            for constraint_obj in field_info.metadata:
                if hasattr(constraint_obj, "gt") and constraint_obj.gt is not None:
                    gt_val = constraint_obj.gt
                if hasattr(constraint_obj, "ge") and constraint_obj.ge is not None:
                    ge_val = constraint_obj.ge
                if hasattr(constraint_obj, "lt") and constraint_obj.lt is not None:
                    lt_val = constraint_obj.lt
                if hasattr(constraint_obj, "le") and constraint_obj.le is not None:
                    le_val = constraint_obj.le
                if hasattr(constraint_obj, "multiple_of") and constraint_obj.multiple_of is not None:
                    multiple_of_val = constraint_obj.multiple_of
                if hasattr(constraint_obj, "min_length") and constraint_obj.min_length is not None:
                    min_length_val = constraint_obj.min_length
                if hasattr(constraint_obj, "max_length") and constraint_obj.max_length is not None:
                    max_length_val = constraint_obj.max_length

    if field_type_to_generate is int:
        min_val_default = 0
        max_val_default = 1000

        min_val = max(min_val_default, ge_val) if ge_val is not None else min_val_default

        if gt_val is not None:
            min_val = max(min_val, gt_val + 1)

        max_val = min(max_val_default, le_val) if le_val is not None else max_val_default

        if lt_val is not None:
            max_val = min(max_val, lt_val - 1)

        if min_val > max_val:
            max_val = min_val

        try:
            if multiple_of_val is not None and multiple_of_val > 0:
                actual_min_multiple = (
                    ((min_val + multiple_of_val - 1) // multiple_of_val * multiple_of_val)
                    if min_val >= 0
                    else (min_val // multiple_of_val * multiple_of_val)
                )
                if actual_min_multiple < min_val and min_val < 0:
                    actual_min_multiple += multiple_of_val
                actual_max_multiple = (max_val // multiple_of_val) * multiple_of_val

                if actual_min_multiple > actual_max_multiple:
                    return random.randint(min_val, max_val)

                num_steps = (actual_max_multiple - actual_min_multiple) // multiple_of_val
                chosen_step = random.randint(0, num_steps)
                return actual_min_multiple + chosen_step * multiple_of_val
            return random.randint(min_val, max_val)
        except ValueError:
            return min_val

    if field_type_to_generate is float:
        min_val_f_default = 0.0
        max_val_f_default = 1000.0

        min_val_f = max(min_val_f_default, ge_val) if ge_val is not None else min_val_f_default
        if gt_val is not None:
            min_val_f = max(min_val_f, gt_val)

        max_val_f = min(max_val_f_default, le_val) if le_val is not None else max_val_f_default
        if lt_val is not None:
            max_val_f = min(max_val_f, lt_val)

        if min_val_f > max_val_f:
            max_val_f = min_val_f

        val_f = random.uniform(min_val_f, max_val_f)

        if gt_val is not None and val_f <= gt_val:
            val_f = min(gt_val + abs(gt_val * 0.000001) + sys.float_info.epsilon, max_val_f)
        if lt_val is not None and val_f >= lt_val:
            val_f = max(lt_val - abs(lt_val * 0.000001) - sys.float_info.epsilon, min_val_f)

        val_f = max(min_val_f, min(val_f, max_val_f))

        if multiple_of_val is not None and multiple_of_val > 0:
            val_f = round(val_f / float(multiple_of_val)) * float(multiple_of_val)
            val_f = max(min_val_f, min(val_f, max_val_f))

        return round(val_f, 2)

    if field_type_to_generate is str:
        min_len = min_length_val if min_length_val is not None else 1
        max_len = max_length_val if max_length_val is not None else 50

        if min_len < 0:
            min_len = 0
        if max_len < 0:
            max_len = 0
        if min_len > max_len:
            min_len = max_len

        if min_len == max_len:
            return faker_instance.pystr(min_chars=min_len, max_chars=max_len) if min_len > 0 else ""

        target_gen_len = random.randint(min_len, max(min_len, max_len + 5))
        if target_gen_len < 5 and max_len > 5:
            target_gen_len = random.randint(min_len, 5)

        text = "" if target_gen_len <= 0 else faker_instance.text(max_nb_chars=target_gen_len + 20)

        text = text[:max_len]

        if len(text) < min_len:
            padding_needed = min_len - len(text)
            padding_chars = "".join(faker_instance.random_letters(length=padding_needed))
            text = text + padding_chars

        return text

    if field_type_to_generate is bool:
        return random.choice([True, False])
    if field_type_to_generate is uuid.UUID:
        return faker_instance.uuid4(cast_to=str)
    if field_type_to_generate is datetime:
        dt_obj = faker_instance.date_time_between(start_date="-10y", end_date="now", tzinfo=UTC)
        return dt_obj.isoformat()
    if field_type_to_generate is date:
        d_obj = faker_instance.date_between(start_date="-10y", end_date="today")
        return d_obj.isoformat()
    if field_type_to_generate is time:
        t_obj = faker_instance.time_object()
        return t_obj.isoformat()
    if isinstance(field_type_to_generate, type) and issubclass(field_type_to_generate, BaseModel):
        return generate_fake_data_for_model(field_type_to_generate, faker_instance_override=faker_instance)
    if field_type_to_generate is Any:
        return "any_value_placeholder"
    return f"unsupported_type_{field_type_to_generate!s}"
