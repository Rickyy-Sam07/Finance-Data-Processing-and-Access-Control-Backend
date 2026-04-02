from datetime import UTC, date, datetime

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.financial_record import FinancialRecord
from app.models.user import User
from app.schemas.record import RecordCreate, RecordUpdate
from app.services.audit_service import create_audit_log
from app.services.event_service import emit_domain_event


def create_record(db: Session, payload: RecordCreate, current_user: User) -> FinancialRecord:
    record = FinancialRecord(
        amount=payload.amount,
        type=payload.type,
        category=payload.category,
        record_date=payload.record_date,
        notes=payload.notes,
        created_by=current_user.id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    create_audit_log(
        db,
        actor_user_id=current_user.id,
        action="record_created",
        resource_type="financial_record",
        resource_id=str(record.id),
        details=f"type={record.type};amount={record.amount}",
    )
    emit_domain_event(
        db,
        event_type="record.created",
        aggregate_type="financial_record",
        aggregate_id=str(record.id),
        payload={
            "id": record.id,
            "amount": record.amount,
            "type": record.type,
            "category": record.category,
            "record_date": str(record.record_date),
            "created_by": record.created_by,
        },
    )
    return record


def get_record_or_404(db: Session, record_id: int, *, include_deleted: bool = False) -> FinancialRecord:
    query = db.query(FinancialRecord).filter(FinancialRecord.id == record_id)
    if not include_deleted:
        query = query.filter(FinancialRecord.is_deleted.is_(False))
    record = query.first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


def update_record(db: Session, record: FinancialRecord, payload: RecordUpdate, current_user: User) -> FinancialRecord:
    if record.is_deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot update a deleted record")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(record, field, value)
    db.add(record)
    db.commit()
    db.refresh(record)
    create_audit_log(
        db,
        actor_user_id=current_user.id,
        action="record_updated",
        resource_type="financial_record",
        resource_id=str(record.id),
        details="record fields updated",
    )
    emit_domain_event(
        db,
        event_type="record.updated",
        aggregate_type="financial_record",
        aggregate_id=str(record.id),
        payload={
            "id": record.id,
            "updated_fields": list(data.keys()),
            "updated_by": current_user.id,
        },
    )
    return record


def delete_record(db: Session, record: FinancialRecord, current_user: User) -> None:
    if record.is_deleted:
        return

    record.is_deleted = True
    record.deleted_at = datetime.now(UTC)
    db.add(record)
    db.commit()
    create_audit_log(
        db,
        actor_user_id=current_user.id,
        action="record_deleted",
        resource_type="financial_record",
        resource_id=str(record.id),
        details="soft delete",
    )
    emit_domain_event(
        db,
        event_type="record.deleted",
        aggregate_type="financial_record",
        aggregate_id=str(record.id),
        payload={"id": record.id, "deleted_by": current_user.id, "deleted_at": record.deleted_at.isoformat()},
    )


def restore_record(db: Session, record: FinancialRecord, current_user: User) -> FinancialRecord:
    if not record.is_deleted:
        return record

    record.is_deleted = False
    record.deleted_at = None
    db.add(record)
    db.commit()
    db.refresh(record)
    create_audit_log(
        db,
        actor_user_id=current_user.id,
        action="record_restored",
        resource_type="financial_record",
        resource_id=str(record.id),
        details="soft restore",
    )
    emit_domain_event(
        db,
        event_type="record.restored",
        aggregate_type="financial_record",
        aggregate_id=str(record.id),
        payload={"id": record.id, "restored_by": current_user.id},
    )
    return record


def filter_records(
    db: Session,
    *,
    start_date: date | None,
    end_date: date | None,
    category: str | None,
    record_type: str | None,
    q: str | None,
    include_deleted: bool,
    skip: int,
    limit: int,
):
    query = db.query(FinancialRecord)
    if not include_deleted:
        query = query.filter(FinancialRecord.is_deleted.is_(False))
    if start_date:
        query = query.filter(FinancialRecord.record_date >= start_date)
    if end_date:
        query = query.filter(FinancialRecord.record_date <= end_date)
    if category:
        query = query.filter(FinancialRecord.category == category)
    if record_type:
        query = query.filter(FinancialRecord.type == record_type)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                FinancialRecord.category.ilike(like),
                FinancialRecord.notes.ilike(like),
                FinancialRecord.type.ilike(like),
            )
        )

    total = query.count()
    records = query.order_by(FinancialRecord.record_date.desc()).offset(skip).limit(limit).all()
    return records, total
