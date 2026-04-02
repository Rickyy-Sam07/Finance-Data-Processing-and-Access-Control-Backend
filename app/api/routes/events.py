from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.models.domain_event import DomainEvent
from app.models.user import User
from app.schemas.events import DomainEventListResponse, RetryEventsResponse
from app.services.event_service import retry_pending_events

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=DomainEventListResponse)
def list_domain_events(
    status: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("events:read")),
) -> DomainEventListResponse:
    query = db.query(DomainEvent)
    if status:
        query = query.filter(DomainEvent.status == status)
    if event_type:
        query = query.filter(DomainEvent.event_type == event_type)

    total = query.count()
    items = query.order_by(DomainEvent.created_at.desc()).offset(skip).limit(limit).all()
    return DomainEventListResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/retry", response_model=RetryEventsResponse)
def retry_events(
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("events:publish")),
) -> RetryEventsResponse:
    return RetryEventsResponse(**retry_pending_events(db, limit=limit))
