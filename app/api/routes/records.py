from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permission
from app.core.database import get_db
from app.models.user import User
from app.schemas.record import RecordCreate, RecordListResponse, RecordResponse, RecordUpdate
from app.services.record_service import (
    create_record,
    delete_record,
    filter_records,
    get_record_or_404,
    restore_record,
    update_record,
)

router = APIRouter(prefix="/records", tags=["records"])


@router.post("", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
def create_record_endpoint(
    payload: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("records:create")),
) -> RecordResponse:
    return create_record(db, payload, current_user)


@router.get("", response_model=RecordListResponse)
def list_records(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    category: str | None = Query(default=None),
    record_type: str | None = Query(default=None, pattern="^(income|expense)$"),
    q: str | None = Query(default=None, min_length=1, max_length=100),
    include_deleted: bool = Query(default=False),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("records:read")),
) -> RecordListResponse:
    effective_include_deleted = include_deleted and current_user.role == "admin"
    items, total = filter_records(
        db,
        start_date=start_date,
        end_date=end_date,
        category=category,
        record_type=record_type,
        q=q,
        include_deleted=effective_include_deleted,
        skip=skip,
        limit=limit,
    )
    return RecordListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/{record_id}", response_model=RecordResponse)
def get_record(
    record_id: int,
    include_deleted: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("records:read")),
) -> RecordResponse:
    effective_include_deleted = include_deleted and current_user.role == "admin"
    return get_record_or_404(db, record_id, include_deleted=effective_include_deleted)


@router.put("/{record_id}", response_model=RecordResponse)
def update_record_endpoint(
    record_id: int,
    payload: RecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("records:update")),
) -> RecordResponse:
    record = get_record_or_404(db, record_id)
    return update_record(db, record, payload, current_user)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record_endpoint(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("records:delete")),
) -> None:
    record = get_record_or_404(db, record_id)
    delete_record(db, record, current_user)


@router.post("/{record_id}/restore", response_model=RecordResponse)
def restore_record_endpoint(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("records:update")),
) -> RecordResponse:
    record = get_record_or_404(db, record_id, include_deleted=True)
    return restore_record(db, record, current_user)
