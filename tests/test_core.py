import pytest
from faker import Faker
from pydantic import BaseModel

from pydantic_faker.core import generate_fake_data_for_model, get_faker_instance, load_pydantic_model

from .helpers import SimpleTestModel


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
    """Check if Faker is used for specific field names."""

    class NameEmailModel(BaseModel):
        name: str
        email: str
        company: str
        random_text: str

    data = generate_fake_data_for_model(NameEmailModel, seed=123)

    faker_ref = Faker()
    Faker.seed(123)
    faker_ref.seed_instance(123)

    assert data["name"] == faker_ref.name()
    assert data["email"] == faker_ref.email()
    assert data["company"] == faker_ref.company()
    assert data["random_text"] == faker_ref.sentence(nb_words=3)


def test_generate_fake_data_deterministic_with_seed():
    seed = 777
    data1 = generate_fake_data_for_model(SimpleTestModel, seed=seed, faker_locale="en_US")
    data2 = generate_fake_data_for_model(SimpleTestModel, seed=seed, faker_locale="en_US")
    assert data1 == data2, "Data generated with the same seed and locale should be identical"

    data3 = generate_fake_data_for_model(SimpleTestModel, seed=seed + 1, faker_locale="en_US")
    assert data1 != data3, "Data generated with different seeds should differ"
