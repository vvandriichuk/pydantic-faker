from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class SimpleUser(BaseModel):
    id: int
    name: str
    is_active: bool
    uuid: UUID
    created_at: datetime
    birth_date: date
    wakeup_time: time
    email: str | None = None
    rating: float | None = Field(default=None)


class NestedItem(BaseModel):
    item_id: str
    value: float
    tags: list[str]


class ComplexOrder(BaseModel):
    order_id: int
    user: SimpleUser
    items: list[NestedItem]
    metadata: dict[str, int] | None = None


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


class ConstrainedListsModel(BaseModel):
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
