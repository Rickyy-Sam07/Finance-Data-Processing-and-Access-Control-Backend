# Finance Data Processing and Access Control Backend

Assessment-ready backend with a lightweight frontend dashboard.

It demonstrates:
- Structured backend architecture (route -> service -> model)
- Role-based access control (viewer, analyst, admin)
- Financial record CRUD + filtering + pagination metadata
- Dashboard analytics APIs
- Structured audit log query APIs
- Event-driven outbox pipeline with optional Kafka publishing
- Login rate limiting
- Migration-driven schema management with Alembic
- Deployment artifacts for Docker/Render

## Tech Stack
- FastAPI
- SQLAlchemy
- Alembic
- SQLite (local default) / PostgreSQL (deployment)
- JWT authentication
- Vanilla JS frontend + Chart.js
- Pytest

## Roles and Access Matrix
- viewer: `dashboard:read`
- analyst: `dashboard:read`, `records:read`
- admin: full records management, user management, audit log read

## API Highlights
- `POST /auth/login` (rate limited)
- `GET /auth/me`
- `GET /dashboard/summary`
- `GET /records` (returns `items`, `total`, `skip`, `limit`, supports `q` text search)
- `POST /records`, `PUT /records/{id}`, `DELETE /records/{id}`
- `POST /records/{id}/restore`
- `POST /users`, `GET /users`, `PATCH /users/{id}/status`, `PATCH /users/{id}/role`
- `GET /audits` with filters (`actor_user_id`, `action`, `resource_type`, `from_ts`, `to_ts`)
- `GET /events` and `POST /events/retry` (admin) for outbox/event pipeline observability

## Local Setup
1. Create and activate venv

```bash
python -m venv .venv
. .venv/Scripts/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Create environment file

```bash
copy .env.example .env
```

4. Apply migrations and seed demo data

```bash
python scripts/seed_data.py
```

5. Run app (port 8001)

```bash
python app/main.py
```

6. Open
- Frontend: http://127.0.0.1:8001/
- Swagger: http://127.0.0.1:8001/docs
- Health: http://127.0.0.1:8001/health

## Demo Credentials
- admin@finance.example.com / Admin@123
- analyst@finance.example.com / Analyst@123
- viewer@finance.example.com / Viewer@123

## Testing
```bash
pytest -q
```

## Migration Commands
```bash
alembic upgrade head
alembic downgrade -1
```

## Deployment Ready Files
- `Dockerfile`
- `.dockerignore`
- `render.yaml`
- `Procfile`

## Deploy to Render (Example)
1. Create a new Web Service from this repo.
2. Render reads `render.yaml` automatically.
3. Add env vars:
   - `JWT_SECRET_KEY`
   - `DATABASE_URL` (PostgreSQL)
4. Deploy.

## Public URLs (Fill after deploy)
- Live App URL: `<add-your-render-url>`
- Public API Docs URL: `<add-your-render-url>/docs`

## Submission Extras
- Architecture diagram: `docs/architecture.md`
- ADR: `docs/adr-001-backend-architecture.md`
- Demo flow script: `docs/demo-script.md`
- Quick API walkthrough helper: `scripts/demo_flow.py`

## Assumptions and Tradeoffs
- Single-tenant scope for clarity.
- One-currency model.
- No external payment integrations.
- In-memory rate limiting is suitable for assessment/demo; distributed rate limiting is recommended for multi-instance production.
- Records use soft delete (`is_deleted`, `deleted_at`) so deleted data can be restored and is excluded from normal list/summary endpoints.
- Event-driven design uses a transactional outbox table (`domain_events`) and optional Kafka fan-out when brokers are configured.

## Event-Driven Architecture Notes
- Record mutations emit domain events (`record.created`, `record.updated`, `record.deleted`, `record.restored`).
- Events are persisted in `domain_events` with status tracking (`pending`, `published`, `skipped`).
- If `KAFKA_BOOTSTRAP_SERVERS` is configured, events are published to `KAFKA_TOPIC`.
- If Kafka is unavailable, events remain in `pending` and can be retried via `POST /events/retry`.

## Frontend Plotting Reliability
- Charts are rendered with built-in SVG (no external chart CDN dependency), so plotting works in offline/restricted networks.
