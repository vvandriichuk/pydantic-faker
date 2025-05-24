from datetime import date, datetime, time
from enum import Enum
from typing import Any, Literal
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


class ConstrainedNumbersModel(BaseModel):
    int_gt: int = Field(gt=10)
    int_ge: int = Field(ge=5)
    int_lt: int = Field(lt=20)
    int_le: int = Field(le=15)
    int_gt_lt: int = Field(gt=100, lt=110)
    int_ge_le: int = Field(ge=50, le=55)
    int_multiple_of: int = Field(multiple_of=7)
    int_all_constraints: int = Field(gt=0, le=100, multiple_of=10)

    float_gt: float = Field(gt=10.5)
    float_ge: float = Field(ge=5.25)
    float_lt: float = Field(lt=20.75)
    float_le: float = Field(le=15.5)
    float_gt_lt: float = Field(gt=100.0, lt=100.1)
    float_ge_le: float = Field(ge=50.0, le=50.5)
    float_multiple_of: float = Field(multiple_of=0.5)
    float_all_constraints: float = Field(gt=1.0, le=10.0, multiple_of=2.5)


class ConstrainedStringsModel(BaseModel):
    str_min_len: str = Field(min_length=5)
    str_max_len: str = Field(max_length=10)
    str_min_max_len: str = Field(min_length=3, max_length=7)


class ConstrainedListsModel(BaseModel):
    list_min_items: list[int] = Field(min_length=2)
    list_max_items: list[str] = Field(max_length=4)
    list_min_max_items: list[bool] = Field(min_length=1, max_length=3)


class StatusEnum(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class AdvancedTypesModel(BaseModel):
    direction: Literal["north", "south", "east", "west"]
    status: StatusEnum
    mixed_type: int | str | bool


class ModelWithExamples(BaseModel):
    status: str = Field(examples=["active", "pending", "archived"])
    priority: int = Field(default=1, examples=[1, 2, 3, 4, 5])
    tags: list[str] = Field(default_factory=list, examples=[["tag1", "tag2"], ["urgent"]])
