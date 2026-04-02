from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogListResponse

router = APIRouter(prefix="/audits", tags=["audits"])


@router.get("", response_model=AuditLogListResponse)
def list_audit_logs(
    actor_user_id: int | None = Query(default=None, ge=1),
    action: str | None = Query(default=None),
    resource_type: str | None = Query(default=None),
    from_ts: datetime | None = Query(default=None),
    to_ts: datetime | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("audits:read")),
) -> AuditLogListResponse:
    query = db.query(AuditLog)
    if actor_user_id is not None:
        query = query.filter(AuditLog.actor_user_id == actor_user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if from_ts:
        query = query.filter(AuditLog.created_at >= from_ts)
    if to_ts:
        query = query.filter(AuditLog.created_at <= to_ts)

    total = query.count()
    items = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return AuditLogListResponse(items=items, total=total, skip=skip, limit=limit)
