import random

import pytest
from faker import Faker
from pydantic import BaseModel

from pydantic_faker.core import generate_fake_data_for_model, get_faker_instance, load_pydantic_model

from .helpers import (
    AdvancedTypesModel,
    ConstrainedListsModel,
    ConstrainedNumbersModel,
    ConstrainedStringsModel,
    ModelWithExamples,
    SimpleTestModel,
    StatusEnum,
)


def test_load_pydantic_model_success():
    """Tests successful loading of a Pydantic model."""
    try:
        model_class = load_pydantic_model("test_models:SimpleUser")
        assert model_class is not None
        assert model_class.__name__ == "SimpleUser"
        assert issubclass(model_class, BaseModel)
    except ImportError:
        pytest.skip(
            "Skipping test_load_pydantic_model_success: test_models.py not found in PYTHONPATH. "
            "Ensure pytest is run from project root or test_models.py is accessible.",
        )
    except Exception as e:
        pytest.fail(f"load_pydantic_model failed unexpectedly: {e}")


def test_load_pydantic_model_module_not_found():
    """Tests loading a model from a non-existent module."""
    from typer import Exit as TyperExit

    with pytest.raises(TyperExit):
        load_pydantic_model("non_existent_module:MyModel")


def test_load_pydantic_model_class_not_found():
    """Tests loading a non-existent class from an existing module."""
    from typer import Exit as TyperExit

    with pytest.raises(TyperExit):
        load_pydantic_model("test_models:NonExistentClass")


def test_load_pydantic_model_not_pydantic():
    """Tests loading a class that is not a Pydantic BaseModel."""
    from typer import Exit as TyperExit

    with pytest.raises(TyperExit):
        load_pydantic_model("tests.helpers:NotPydanticModel")


def test_get_faker_instance_default():
    f = get_faker_instance()
    assert isinstance(f, Faker)


def test_get_faker_instance_with_locale():
    locale = "ja_JP"
    f = get_faker_instance(locale=locale)
    assert isinstance(f, Faker)
    name_sample = f.name()
    assert any(ord(c) > 127 for c in name_sample), (
        f"Name '{name_sample}' should contain non-ASCII characters for ja_JP locale"
    )


def test_get_faker_instance_with_seed():
    seed = 42
    f1 = get_faker_instance(seed=seed)
    f2 = get_faker_instance(seed=seed)

    assert f1.name() == f2.name(), "Faker instances with the same seed should produce the same name"
    assert f1.address() == f2.address(), "Faker instances with the same seed should produce the same address"

    f3 = get_faker_instance(seed=99)
    assert f1.name() != f3.name(), "Faker instances with different seeds should produce different data"


def test_generate_fake_data_uses_faker_names():
    """Check if Faker is used for specific field names and that unmapped str fields are also deterministic with seed."""

    class NameEmailModel(BaseModel):
        name: str
        email: str
        company: str
        random_text: str

    seed_value = 123

    data1 = generate_fake_data_for_model(NameEmailModel, seed=seed_value)

    data2 = generate_fake_data_for_model(NameEmailModel, seed=seed_value)

    assert data1["name"] == data2["name"]
    assert data1["email"] == data2["email"]
    assert data1["company"] == data2["company"]

    assert data1["random_text"] == data2["random_text"]

    assert isinstance(data1["random_text"], str)
    assert len(data1["random_text"]) > 0
    assert data1["random_text"] != data1["name"]
    assert not data1["random_text"].startswith("random_string_")

    faker_ref = Faker()
    Faker.seed(seed_value)
    faker_ref.seed_instance(seed_value)

    expected_name = faker_ref.name()
    expected_email = faker_ref.email()
    expected_company = faker_ref.company()

    assert data1["name"] == expected_name
    assert data1["email"] == expected_email
    assert data1["company"] == expected_company


def test_generate_fake_data_deterministic_with_seed():
    seed = 777
    data1 = generate_fake_data_for_model(SimpleTestModel, seed=seed, faker_locale="en_US")
    data2 = generate_fake_data_for_model(SimpleTestModel, seed=seed, faker_locale="en_US")
    assert data1 == data2, "Data generated with the same seed and locale should be identical"

    data3 = generate_fake_data_for_model(SimpleTestModel, seed=seed + 1, faker_locale="en_US")
    assert data1 != data3, "Data generated with different seeds should differ"


def test_generate_int_constraints():
    for _ in range(10):
        data = generate_fake_data_for_model(ConstrainedNumbersModel, seed=random.randint(1, 10000))
        assert data["int_gt"] > 10
        assert data["int_ge"] >= 5
        assert data["int_lt"] < 20
        assert data["int_le"] <= 15
        assert 100 < data["int_gt_lt"] < 110
        assert 50 <= data["int_ge_le"] <= 55
        assert data["int_multiple_of"] % 7 == 0

        value_int_all = data["int_all_constraints"]
        assert value_int_all > 0
        assert value_int_all <= 100
        assert value_int_all % 10 == 0


def test_generate_float_constraints():
    for _ in range(10):
        data = generate_fake_data_for_model(ConstrainedNumbersModel, seed=random.randint(1, 10000))
        assert data["float_gt"] > 10.5
        assert data["float_ge"] >= 5.25
        assert data["float_lt"] < 20.75
        assert data["float_le"] <= 15.5
        assert 100.0 < data["float_gt_lt"] < 100.1
        assert 50.0 <= data["float_ge_le"] <= 50.5
        import math

        assert math.isclose(data["float_multiple_of"] % 0.5, 0.0) or math.isclose(data["float_multiple_of"] % 0.5, 0.5)

        value_float_all = data["float_all_constraints"]
        assert value_float_all > 1.0
        assert value_float_all <= 10.0
        import math

        assert math.isclose(value_float_all % 2.5, 0.0) or math.isclose(value_float_all % 2.5, 2.5)


def test_generate_string_constraints():
    for _ in range(10):
        data = generate_fake_data_for_model(ConstrainedStringsModel, seed=random.randint(1, 10000))
        assert len(data["str_min_len"]) >= 5
        assert len(data["str_max_len"]) <= 10
        assert 3 <= len(data["str_min_max_len"]) <= 7


def test_generate_list_constraints():
    for _ in range(10):
        data = generate_fake_data_for_model(ConstrainedListsModel, seed=random.randint(1, 10000))
        assert len(data["list_min_items"]) >= 2
        assert len(data["list_max_items"]) <= 4
        assert 1 <= len(data["list_min_max_items"]) <= 3
        assert all(isinstance(x, int) for x in data["list_min_items"])
        assert all(isinstance(x, str) for x in data["list_max_items"])
        assert all(isinstance(x, bool) for x in data["list_min_max_items"])


def test_generate_literal_type():
    """Tests generation for Literal types."""
    possible_directions = {"north", "south", "east", "west"}
    generated_directions = set()
    for i in range(20):
        data = generate_fake_data_for_model(AdvancedTypesModel, seed=i)
        assert "direction" in data
        assert data["direction"] in possible_directions
        generated_directions.add(data["direction"])
    assert len(generated_directions) > 1, "Should generate multiple different literal values over iterations"
    if len(possible_directions) <= 20:
        assert generated_directions == possible_directions, "Should eventually generate all literal values"


def test_generate_enum_type():
    """Tests generation for Enum types."""
    possible_status_values = {member.value for member in StatusEnum}
    generated_statuses = set()
    for i in range(20):
        data = generate_fake_data_for_model(AdvancedTypesModel, seed=i)
        assert "status" in data
        assert data["status"] in possible_status_values
        generated_statuses.add(data["status"])
    assert len(generated_statuses) > 1, "Should generate multiple different enum values over iterations"
    if len(possible_status_values) <= 20:
        assert generated_statuses == possible_status_values, "Should eventually generate all enum values"


def test_generate_union_type():
    """Tests generation for Union[int, str, bool] types."""
    generated_types = set()
    found_int = False
    found_str = False
    found_bool = False

    for i in range(50):
        data = generate_fake_data_for_model(AdvancedTypesModel, seed=i)
        assert "mixed_type" in data
        value = data["mixed_type"]

        is_valid_type = isinstance(value, int | str | bool)
        assert is_valid_type, f"Generated type {type(value)} is not in Union[int, str, bool]"

        if isinstance(value, int):
            found_int = True
        if isinstance(value, str):
            found_str = True
        if isinstance(value, bool):
            found_bool = True

        generated_types.add(type(value))

    assert int in generated_types, "Integer type was not generated for Union"
    assert str in generated_types, "String type was not generated for Union"
    assert bool in generated_types, "Boolean type was not generated for Union"

    assert found_int, "Integer type was not generated for Union"
    assert found_str, "String type was not generated for Union"
    assert found_bool, "Boolean type was not generated for Union"


def test_generate_uses_field_examples():
    model_class = ModelWithExamples
    example_field_name = "status"
    possible_examples = set(model_class.model_fields[example_field_name].examples or [])

    generated_from_examples_count = 0
    generated_other_count = 0
    total_runs = 200

    for i in range(total_runs):
        data = generate_fake_data_for_model(model_class, seed=i)
        generated_value = data[example_field_name]

        if generated_value in possible_examples:
            generated_from_examples_count += 1
        else:
            generated_other_count += 1
            assert isinstance(generated_value, str)

    assert generated_from_examples_count > 0, "No values were generated from examples list"
    assert generated_other_count > 0, "Only values from examples list were generated"

    print(f"Generated from examples: {generated_from_examples_count}/{total_runs}")
