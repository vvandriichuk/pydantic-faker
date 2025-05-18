from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, Field


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
    tags: list[str]  # Изменил на List[str]


class ComplexOrder(BaseModel):
    order_id: int
    user: SimpleUser
    items: list[NestedItem]  # Изменил на List[NestedItem]
    metadata: dict[str, int] | None = None
