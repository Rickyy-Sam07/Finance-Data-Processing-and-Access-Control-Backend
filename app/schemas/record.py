from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class RecordCreate(BaseModel):
    amount: float = Field(gt=0)
    type: str = Field(pattern="^(income|expense)$")
    category: str = Field(min_length=2, max_length=100)
    record_date: date
    notes: str | None = Field(default=None, max_length=500)


class RecordUpdate(BaseModel):
    amount: float | None = Field(default=None, gt=0)
    type: str | None = Field(default=None, pattern="^(income|expense)$")
    category: str | None = Field(default=None, min_length=2, max_length=100)
    record_date: date | None = None
    notes: str | None = Field(default=None, max_length=500)


class RecordResponse(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    record_date: date
    notes: str | None
    is_deleted: bool
    deleted_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecordListResponse(BaseModel):
    items: list[RecordResponse]
    total: int
    skip: int
    limit: int
