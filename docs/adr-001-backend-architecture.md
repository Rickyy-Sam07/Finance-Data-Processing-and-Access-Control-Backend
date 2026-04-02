# ADR-001: Layered FastAPI + SQLAlchemy + Alembic

## Status
Accepted

## Context
The assessment requires clear backend structure, RBAC, reliable persistence, and maintainable logic. The system should be deployable quickly while demonstrating architecture maturity.

## Decision
Use a layered architecture:
- API routes for transport concerns and permission boundaries.
- Services for business logic and aggregation.
- SQLAlchemy ORM models for persistence.
- Alembic for schema migrations.
- JWT auth with RBAC policy map.

## Consequences
Positive:
- Clear separation of concerns and testability.
- Migration-driven schema control for deployment environments.
- Easy to extend with additional policies and analytics.

Tradeoff:
- Slightly more files/boilerplate than a single-file prototype.
