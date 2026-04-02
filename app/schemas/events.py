from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DomainEventResponse(BaseModel):
    id: int
    event_type: str
    aggregate_type: str
    aggregate_id: str
    payload: str
    status: str
    error: str | None
    published_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DomainEventListResponse(BaseModel):
    items: list[DomainEventResponse]
    total: int
    skip: int
    limit: int


class RetryEventsResponse(BaseModel):
    processed: int
    published: int
    still_pending: int
