from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    *,
    actor_user_id: int,
    action: str,
    resource_type: str,
    resource_id: str,
    details: str | None = None,
) -> None:
    log = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
    )
    db.add(log)
    db.commit()
