# Architecture Diagram

```mermaid
flowchart LR
    U[Frontend Dashboard] -->|JWT login| A[/auth/login]
    U -->|Bearer token| R[/records]
    U -->|Bearer token| D[/dashboard/summary]
    U -->|Bearer token| M[/users]
    U -->|Bearer token| L[/audits]

    A --> S[Auth + RBAC Layer]
    R --> S
    D --> S
    M --> S
    L --> S

    S --> B[Service Layer]
    B --> DB[(PostgreSQL or SQLite)]
    B --> AL[(Audit Logs)]

    MIG[Alembic Migrations] --> DB
```

## Design Notes
- API layer enforces permission gates.
- Service layer handles business logic and audit writes.
- Migration layer handles schema lifecycle for deployment consistency.
- Frontend is static and served by FastAPI for simple deployment.
