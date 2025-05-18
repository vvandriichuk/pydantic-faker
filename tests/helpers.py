from datetime import date, datetime, time
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class SimpleTestModel(BaseModel):
    """
    A simple Pydantic model for basic testing.
    Includes a variety of common field types.
    """

    id: int
    name: str  # Expect Faker to generate a name
    email: EmailStr  # Expect Faker to generate an email (due to type or name)
    is_active: bool
    uuid: UUID
    created_at: datetime
    birth_date: date
    wakeup_time: time
    description: str  # Should use generic Faker sentence
    website: HttpUrl | None = None  # Expect Faker to generate a URL or None
    rating: float | None = Field(default=None)
    tags: list[str]
    metadata: dict[str, Any] | None = None


class NestedModel(BaseModel):
    """
    A model intended to be nested within another model.
    """

    nested_id: int
    nested_name: str
    value: float | None = None


class ComplexTestModel(BaseModel):
    """
    A more complex model featuring nesting and collections of models.
    """

    order_id: str  # Changed to str to see if Faker handles it as a generic sentence
    user_details: SimpleTestModel  # Nested model
    items: list[NestedModel]  # List of nested models
    configuration: dict[str, bool]
    notes: str | None = "Default notes"  # Field with a default


class NotPydanticModel:
    """
    A simple class that is NOT a Pydantic BaseModel, used for testing error handling.
    """

    field_one: str
    field_two: int

    def __init__(self, field_one: str, field_two: int):
        self.field_one = field_one
        self.field_two = field_two


class ModelWithPydanticTypes(BaseModel):
    contact_email: EmailStr
    personal_website: HttpUrl
    generic_link: str
