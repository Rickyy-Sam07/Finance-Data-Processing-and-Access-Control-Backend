import json
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.domain_event import DomainEvent


def _try_publish_to_kafka(event: DomainEvent) -> tuple[bool, str | None]:
    if not settings.kafka_bootstrap_servers:
        return False, "kafka_not_configured"

    try:
        from kafka import KafkaProducer  # type: ignore
    except Exception as exc:  # pragma: no cover
        return False, f"kafka_dependency_missing:{exc}"

    try:
        producer = KafkaProducer(
            bootstrap_servers=[x.strip() for x in settings.kafka_bootstrap_servers.split(",") if x.strip()],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            request_timeout_ms=3000,
        )
        payload = {
            "event_id": event.id,
            "event_type": event.event_type,
            "aggregate_type": event.aggregate_type,
            "aggregate_id": event.aggregate_id,
            "payload": json.loads(event.payload),
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }
        producer.send(settings.kafka_topic, payload)
        producer.flush(timeout=5)
        producer.close()
        return True, None
    except Exception as exc:  # pragma: no cover
        return False, str(exc)


def emit_domain_event(
    db: Session,
    *,
    event_type: str,
    aggregate_type: str,
    aggregate_id: str,
    payload: dict,
) -> DomainEvent:
    if not settings.enable_event_driven_pipeline:
        event = DomainEvent(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload=json.dumps(payload),
            status="skipped",
            error="event_pipeline_disabled",
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    event = DomainEvent(
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        payload=json.dumps(payload),
        status="pending",
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    success, error = _try_publish_to_kafka(event)
    if success:
        event.status = "published"
        event.error = None
        event.published_at = datetime.now(UTC)
    else:
        event.status = "pending"
        event.error = error
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def retry_pending_events(db: Session, limit: int = 50) -> dict[str, int]:
    pending = (
        db.query(DomainEvent)
        .filter(DomainEvent.status == "pending")
        .order_by(DomainEvent.created_at.asc())
        .limit(limit)
        .all()
    )

    published = 0
    failed = 0
    for event in pending:
        success, error = _try_publish_to_kafka(event)
        if success:
            event.status = "published"
            event.error = None
            event.published_at = datetime.now(UTC)
            published += 1
        else:
            event.status = "pending"
            event.error = error
            failed += 1
        db.add(event)
    db.commit()

    return {"processed": len(pending), "published": published, "still_pending": failed}
